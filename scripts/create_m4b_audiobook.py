#!/usr/bin/env python3
"""
Create an M4B audiobook from individual chapter M4A files.
Combines all chapter M4A files into a single M4B file with embedded metadata,
chapter markers, and cover art using a single-pass approach with codec copy
for fast processing.
"""

import sys
import re
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub not installed. Run: uv pip install pydub")
    print("Note: You may also need ffmpeg installed on your system")
    sys.exit(1)


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def find_chapter_files(audiobooks_dir: Path) -> List[Path]:
    """
    Find all chapter M4A files in the audiobooks directory.

    Args:
        audiobooks_dir: Path to audiobooks directory

    Returns:
        Sorted list of M4A file paths
    """
    # Find all M4A files that match the chapter naming pattern (###-Title.m4a)
    m4a_files = sorted(audiobooks_dir.glob("[0-9][0-9][0-9]-*.m4a"))
    return m4a_files


def extract_chapter_title(audio_path: Path) -> str:
    """
    Extract chapter title from audio filename.

    Args:
        audio_path: Path to audio file

    Returns:
        Chapter title (e.g., "The Bridge and the Bloodline")
    """
    # Remove the ###- prefix and file extension
    filename = audio_path.stem  # Gets filename without extension
    match = re.match(r'^\d{3}-(.+)$', filename)
    if match:
        return match.group(1)
    return filename


def get_chapter_duration(audio_path: Path) -> float:
    """
    Get the duration of an audio file in seconds.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds
    """
    audio = AudioSegment.from_file(str(audio_path))
    return len(audio) / 1000.0  # Convert milliseconds to seconds


def build_chapter_list(audio_files: List[Path]) -> List[Dict[str, Any]]:
    """
    Build chapter list with titles and timestamps.

    Args:
        audio_files: List of audio file paths

    Returns:
        List of chapter dictionaries with id, title, start, and end times
    """
    chapters = []
    current_time = 0.0

    for i, audio_path in enumerate(audio_files):
        # Extract chapter number from filename (###-Title.m4a)
        filename = audio_path.stem
        match = re.match(r'^(\d{3})-(.+)$', filename)
        if match:
            chapter_num = int(match.group(1))  # Convert to int to remove zero-padding
            chapter_title = match.group(2)
            # Format as "1 - Title", "13 - Title", etc.
            title = f"{chapter_num} - {chapter_title}"
        else:
            # Fallback if filename doesn't match expected pattern
            title = extract_chapter_title(audio_path)

        duration = get_chapter_duration(audio_path)

        chapters.append({
            "id": i,
            "title": title,
            "start": current_time,
            "end": current_time + duration
        })

        current_time += duration

    return chapters


def load_metadata(metadata_path: Path) -> Dict[str, Any]:
    """
    Load metadata from JSON file.

    Args:
        metadata_path: Path to metadata.json

    Returns:
        Metadata dictionary
    """
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_ffmpeg_metadata_file(chapters: List[Dict[str, Any]], temp_dir: Path) -> Path:
    """
    Create ffmpeg metadata file for chapter markers.

    Args:
        chapters: List of chapter dictionaries
        temp_dir: Temporary directory for metadata file

    Returns:
        Path to metadata file
    """
    metadata_path = temp_dir / "chapters.txt"

    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(";FFMETADATA1\n")
        for chapter in chapters:
            # Convert seconds to milliseconds for ffmpeg
            start_ms = int(chapter['start'] * 1000)
            end_ms = int(chapter['end'] * 1000)

            f.write("\n[CHAPTER]\n")
            f.write(f"TIMEBASE=1/1000\n")
            f.write(f"START={start_ms}\n")
            f.write(f"END={end_ms}\n")
            f.write(f"title={chapter['title']}\n")

    return metadata_path


def create_concat_file(audio_files: List[Path], temp_dir: Path) -> Path:
    """
    Create ffmpeg concat file listing all audio files to combine.

    Args:
        audio_files: List of audio file paths
        temp_dir: Temporary directory for concat file

    Returns:
        Path to concat file
    """
    concat_path = temp_dir / "concat.txt"

    with open(concat_path, 'w', encoding='utf-8') as f:
        for audio_path in audio_files:
            # Use absolute paths and escape special characters
            abs_path = audio_path.absolute()
            # Escape single quotes for ffmpeg
            escaped_path = str(abs_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    return concat_path


def create_m4b(audio_files: List[Path], chapters: List[Dict[str, Any]],
               metadata: Dict[str, Any], cover_path: Path,
               output_path: Path) -> bool:
    """
    Create M4B audiobook file from M4A chapters.

    Args:
        audio_files: List of M4A file paths
        chapters: List of chapter dictionaries
        metadata: Metadata dictionary
        cover_path: Path to cover image
        output_path: Path for output M4B file

    Returns:
        True if successful
    """
    print(f"\nCreating M4B audiobook...")
    print(f"  Combining {len(audio_files)} chapters")
    print(f"  Total duration: {chapters[-1]['end'] / 3600:.2f} hours")

    # Create temporary directory for ffmpeg metadata files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create concat file
        concat_file = create_concat_file(audio_files, temp_path)

        # Create chapter metadata file
        chapter_file = create_ffmpeg_metadata_file(chapters, temp_path)

        # Single-pass ffmpeg command: concatenate, add chapters, cover art, and metadata
        # This is much faster than the old two-pass approach since we use -c:a copy
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),      # Input: concatenated audio files
            "-i", str(chapter_file),     # Input: chapter metadata
            "-i", str(cover_path),       # Input: cover art
            "-map", "0:a",               # Map audio from concat input
            "-map", "2:v",               # Map cover image
            "-c:a", "copy",              # Copy audio codec (no re-encoding!)
            "-c:v", "png",               # Cover art codec
            "-disposition:v:0", "attached_pic",  # Mark cover as attached picture
            "-map_metadata", "1",        # Use chapter metadata
        ]

        # Add metadata tags
        if metadata.get('title'):
            cmd.extend(["-metadata", f"title={metadata['title']}"])

        if metadata.get('authors') and len(metadata['authors']) > 0:
            cmd.extend(["-metadata", f"artist={metadata['authors'][0]}"])
            cmd.extend(["-metadata", f"album_artist={metadata['authors'][0]}"])

        if metadata.get('description'):
            # Remove HTML tags from description
            description = re.sub(r'<[^>]+>', '', metadata['description'])
            cmd.extend(["-metadata", f"comment={description}"])

        if metadata.get('publishedYear'):
            cmd.extend(["-metadata", f"date={metadata['publishedYear']}"])

        if metadata.get('genres') and len(metadata['genres']) > 0:
            cmd.extend(["-metadata", f"genre={', '.join(metadata['genres'])}"])

        if metadata.get('publisher'):
            cmd.extend(["-metadata", f"publisher={metadata['publisher']}"])

        # Set media type to audiobook
        cmd.extend(["-metadata", "media_type=2"])  # 2 = Audiobook

        # Output file
        cmd.extend(["-f", "mp4", str(output_path)])

        print("  Processing audiobook (single pass with copy codec)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating M4B: {result.stderr}")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create M4B audiobook from chapter M4A files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script combines all chapter M4A files in audiobooks/ into a single M4B file.

Required files:
- audiobooks/###-Chapter Title.m4a (chapter files with AAC audio)
- audiobooks/metadata.json (title, author, description, etc.)
- audiobooks/cover.png (cover artwork)

Output:
- audiobooks/Tales-from-Teghrims-Crossing.m4b

The script uses a single-pass approach with -c:a copy for fast processing.
        """
    )
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be generated without doing it")
    parser.add_argument("--force", action="store_true",
                       help="Overwrite existing M4B file")

    args = parser.parse_args()

    # Check for ffmpeg
    if not check_ffmpeg():
        print("Error: ffmpeg not found")
        print("Install ffmpeg: apt-get install ffmpeg")
        sys.exit(1)

    # Get paths
    project_root = Path(__file__).parent.parent
    audiobooks_dir = project_root / "audiobooks"
    metadata_path = audiobooks_dir / "metadata.json"
    cover_path = audiobooks_dir / "cover.png"

    # Validate required files
    if not audiobooks_dir.exists():
        print(f"Error: Audiobooks directory not found: {audiobooks_dir}")
        sys.exit(1)

    if not metadata_path.exists():
        print(f"Error: Metadata file not found: {metadata_path}")
        sys.exit(1)

    if not cover_path.exists():
        print(f"Error: Cover image not found: {cover_path}")
        sys.exit(1)

    # Find chapter M4A files
    audio_files = find_chapter_files(audiobooks_dir)
    if not audio_files:
        print("Error: No chapter M4A files found in audiobooks/")
        print("Expected files matching pattern: ###-Chapter Title.m4a")
        sys.exit(1)

    print(f"Found {len(audio_files)} chapter files:")
    for audio_path in audio_files:
        print(f"  {audio_path.name}")

    # Build chapter list
    print("\nAnalyzing chapters...")
    chapters = build_chapter_list(audio_files)

    print("\nChapter breakdown:")
    for chapter in chapters:
        duration_min = (chapter['end'] - chapter['start']) / 60
        print(f"  Chapter {chapter['id'] + 1}: {chapter['title']} ({duration_min:.1f} min)")

    # Load metadata
    metadata = load_metadata(metadata_path)

    # Determine output filename from title
    title = metadata.get('title', 'Audiobook')
    # Clean title for filename (remove spaces, special chars)
    clean_title = re.sub(r'[^\w\s-]', '', title)
    clean_title = re.sub(r'[-\s]+', '-', clean_title)
    output_filename = f"{clean_title}.m4b"
    output_path = audiobooks_dir / output_filename

    print(f"\nOutput file: {output_path}")
    print(f"Title: {metadata.get('title', 'N/A')}")
    print(f"Author: {metadata.get('authors', ['N/A'])[0] if metadata.get('authors') else 'N/A'}")
    print(f"Total duration: {chapters[-1]['end'] / 3600:.2f} hours")

    if args.dry_run:
        print("\nDry run - no M4B file created")
        print("\nMetadata to be embedded:")
        print(json.dumps(metadata, indent=2))
        sys.exit(0)

    # Check if output file exists
    if output_path.exists() and not args.force:
        print(f"\nError: Output file already exists: {output_path}")
        print("Use --force to overwrite")
        sys.exit(1)

    # Create M4B file
    success = create_m4b(audio_files, chapters, metadata, cover_path, output_path)

    if success:
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\n✅ M4B audiobook created successfully!")
        print(f"   File: {output_path}")
        print(f"   Size: {file_size:.1f} MB")
    else:
        print(f"\n❌ Failed to create M4B audiobook")
        sys.exit(1)


if __name__ == "__main__":
    main()
