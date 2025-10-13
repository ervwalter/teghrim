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
from typing import List, Dict, Any, Optional


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_ffprobe() -> bool:
    """Check if ffprobe is available."""
    try:
        result = subprocess.run(["ffprobe", "-version"], capture_output=True, check=False)
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
    filename = audio_path.stem  # Gets filename without extension
    match = re.match(r'^\d{3}-(.+)$', filename)
    if match:
        return match.group(1)
    return filename


def ffprobe_duration_seconds(audio_path: Path) -> float:
    """
    Get duration using ffprobe without decoding the file.
    """
    r = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "json", str(audio_path)],
        capture_output=True, text=True, check=True
    )
    data = json.loads(r.stdout)
    return float(data["format"]["duration"])


def get_chapter_duration(audio_path: Path) -> float:
    """
    Wrapper in case we later swap duration method.
    """
    return ffprobe_duration_seconds(audio_path)


def build_chapter_list(audio_files: List[Path]) -> List[Dict[str, Any]]:
    """
    Build chapter list with titles and timestamps.

    Args:
        audio_files: List of audio file paths

    Returns:
        List of chapter dictionaries with id, title, start, and end times
    """
    chapters: List[Dict[str, Any]] = []
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
            f.write("TIMEBASE=1/1000\n")
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
            abs_path = audio_path.absolute()
            # Use single quotes and escape single quotes inside paths for POSIX ffmpeg
            escaped_path = str(abs_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    return concat_path


def run_ffmpeg(cmd: List[str], quiet: bool = False) -> int:
    """
    Run ffmpeg command streaming progress to stdout.
    Returns the ffmpeg return code.
    """
    # Let ffmpeg output directly to terminal to avoid pipe buffering issues
    # ffmpeg automatically detects if it's connected to a terminal for progress display
    if quiet:
        # Suppress most output but allow errors through
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    else:
        # Let ffmpeg output directly to terminal for live progress
        result = subprocess.run(cmd)
        return result.returncode


def create_m4b(audio_files: List[Path], chapters: List[Dict[str, Any]],
               metadata: Dict[str, Any], cover_path: Path,
               output_path: Path, quiet: bool = False) -> bool:
    """
    Create M4B audiobook file from M4A chapters.

    Args:
        audio_files: List of M4A file paths
        chapters: List of chapter dictionaries
        metadata: Metadata dictionary
        cover_path: Path to cover image (PNG or JPEG recommended)
        output_path: Path for output M4B file
        quiet: Reduce ffmpeg chatter if True

    Returns:
        True if successful
    """
    print(f"\nCreating M4B audiobook...")
    print(f"  Combining {len(audio_files)} chapters")
    total_hours = chapters[-1]['end'] / 3600.0 if chapters else 0.0
    print(f"  Total duration: {total_hours:.2f} hours")

    # Create temporary directory for ffmpeg metadata files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create concat file
        concat_file = create_concat_file(audio_files, temp_path)

        # Create chapter metadata file
        chapter_file = create_ffmpeg_metadata_file(chapters, temp_path)

        # FFmpeg command: concatenate, add chapters, cover art, and metadata (single pass, copy codecs)
        cmd: List[str] = [
            "ffmpeg",
            "-y",  # Force overwrite without prompting
            "-hide_banner",
            "-v", "warning" if quiet else "info",  # Reduced verbosity to prevent pipe buffer issues
            "-stats",

            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),      # 0: concatenated audio list
            "-i", str(chapter_file),     # 1: chapter metadata (ffmetadata)
            "-i", str(cover_path),       # 2: cover art

            "-map", "0:a",               # Map audio from concat input
            "-map", "2:v",               # Map cover image
            "-c:a", "copy",              # Copy audio codec (no re-encoding)
            "-c:v", "copy",              # Copy image as-is (PNG/JPEG)
            "-disposition:v:0", "attached_pic",  # Mark cover as attached picture

            "-map_metadata", "1",        # Use metadata from input #1
            "-map_chapters", "1",        # Use chapters from input #1

            "-movflags", "+faststart",   # Better playback behavior
            "-f", "mp4", str(output_path)
        ]

        # Add metadata tags
        def add_meta(key: str, value: Optional[str]):
            if value is not None and value != "":
                cmd.extend(["-metadata", f"{key}={value}"])

        title = metadata.get('title')
        if isinstance(title, str):
            add_meta("title", title)

        authors = metadata.get('authors')
        if isinstance(authors, list) and authors:
            add_meta("artist", authors[0])
            add_meta("album_artist", authors[0])

        description = metadata.get('description')
        if isinstance(description, str):
            # Remove HTML tags from description
            description_clean = re.sub(r'<[^>]+>', '', description)
            add_meta("comment", description_clean)

        publishedYear = metadata.get('publishedYear')
        if isinstance(publishedYear, (int, str)):
            add_meta("date", str(publishedYear))

        genres = metadata.get('genres')
        if isinstance(genres, list) and genres:
            add_meta("genre", ", ".join(map(str, genres)))

        publisher = metadata.get('publisher')
        if isinstance(publisher, str):
            add_meta("publisher", publisher)

        # Set media type to audiobook
        add_meta("media_type", "2")  # 2 = Audiobook (common convention)

        print("  Processing audiobook (single pass with copy codec)...")
        rc = run_ffmpeg(cmd, quiet=quiet)
        if rc != 0:
            print("Error creating M4B (ffmpeg exited with non-zero status).")
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
- audiobooks/cover.png (or .jpg) (cover artwork)

Output:
- audiobooks/<Title>.m4b

The script uses a single-pass approach with -c:a copy for fast processing.
        """
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without doing it")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing M4B file")
    parser.add_argument("--quiet", action="store_true",
                        help="Reduce ffmpeg verbosity (still shows progress/errors)")

    args = parser.parse_args()

    # Check for ffmpeg/ffprobe
    if not check_ffmpeg():
        print("Error: ffmpeg not found")
        print("Install ffmpeg (e.g., apt-get install ffmpeg or brew install ffmpeg)")
        sys.exit(1)
    if not check_ffprobe():
        print("Error: ffprobe not found")
        print("Install ffprobe (usually part of ffmpeg package)")
        sys.exit(1)

    # Get paths
    project_root = Path(__file__).parent.parent
    audiobooks_dir = project_root / "audiobooks"
    metadata_path = audiobooks_dir / "metadata.json"
    # Prefer PNG/JPG; change if your project uses another filename
    cover_path_png = audiobooks_dir / "cover.png"
    cover_path_jpg = audiobooks_dir / "cover.jpg"
    cover_path_jpeg = audiobooks_dir / "cover.jpeg"

    # Validate required files
    if not audiobooks_dir.exists():
        print(f"Error: Audiobooks directory not found: {audiobooks_dir}")
        sys.exit(1)

    if not metadata_path.exists():
        print(f"Error: Metadata file not found: {metadata_path}")
        sys.exit(1)

    cover_path: Optional[Path] = None
    for c in (cover_path_png, cover_path_jpg, cover_path_jpeg):
        if c.exists():
            cover_path = c
            break
    if cover_path is None:
        print(f"Error: Cover image not found. Tried: {cover_path_png}, {cover_path_jpg}, {cover_path_jpeg}")
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
    print("\nAnalyzing chapters (ffprobe, no decoding)...")
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
    clean_title = re.sub(r'[^\w\s-]', '', str(title))
    clean_title = re.sub(r'[-\s]+', '-', clean_title).strip('-')
    output_filename = f"{clean_title or 'Audiobook'}.m4b"
    output_path = audiobooks_dir / output_filename

    print(f"\nOutput file: {output_path}")
    print(f"Title: {metadata.get('title', 'N/A')}")
    author_display = 'N/A'
    if isinstance(metadata.get('authors'), list) and metadata['authors']:
        author_display = metadata['authors'][0]
    print(f"Author: {author_display}")
    total_hours = chapters[-1]['end'] / 3600.0 if chapters else 0.0
    print(f"Total duration: {total_hours:.2f} hours")

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
    success = create_m4b(audio_files, chapters, metadata, cover_path, output_path, quiet=args.quiet)

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
