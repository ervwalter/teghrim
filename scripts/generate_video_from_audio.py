#!/usr/bin/env python3
"""
Generate video from audiobook MP3 and static image using ffmpeg.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import re


def clean_for_filename(text: str) -> str:
    """Clean text to be safe for use in a filename."""
    # Remove invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Limit length
    if len(text) > 100:
        text = text[:100].rstrip()
    return text


def generate_video(audio_path: Path, image_path: Path, output_path: Path, 
                  chapter_num: int, title: str) -> bool:
    """
    Generate a video from audio and static image using ffmpeg.
    
    Args:
        audio_path: Path to the MP3 audio file
        image_path: Path to the static image
        output_path: Path for the output video
        chapter_num: Chapter number for metadata
        title: Chapter title for metadata
        
    Returns:
        bool: True if successful
    """
    # Check inputs exist
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        return False
        
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-loop', '1',  # Loop the image
        '-i', str(image_path),  # Input image
        '-i', str(audio_path),  # Input audio
        '-c:v', 'libx264',  # Video codec
        '-tune', 'stillimage',  # Optimize for still image
        '-c:a', 'aac',  # Audio codec
        '-b:a', '192k',  # Audio bitrate
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        '-shortest',  # Match video length to audio
        '-metadata', f'title=Chapter {chapter_num}: {title}',  # Add metadata
        '-metadata', f'track={chapter_num}',
        '-y',  # Overwrite output file if exists
        str(output_path)
    ]
    
    print(f"Generating video: {output_path.name}")
    print(f"  Audio: {audio_path.name}")
    print(f"  Image: {image_path.name}")
    
    try:
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Video created successfully: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ffmpeg: {e}")
        if e.stderr:
            print(f"ffmpeg error output:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Error: ffmpeg not found. Please install ffmpeg.")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate video from audiobook MP3 and static image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script combines an audiobook MP3 with a static image to create a video
suitable for upload to YouTube or other video sharing platforms.

The video will have:
- The static image displayed for the entire duration
- The audiobook as the audio track
- Metadata with chapter number and title
        """
    )
    
    parser.add_argument("audio", type=Path, help="Path to the audiobook MP3 file")
    parser.add_argument("image", type=Path, help="Path to the static image")
    parser.add_argument("--chapter", type=int, required=True, help="Chapter number")
    parser.add_argument("--title", required=True, help="Chapter title")
    parser.add_argument("--output", type=Path, help="Output video path (default: videos/video-YYYY-MM-DD-NNN-Title.mp4)")
    
    args = parser.parse_args()
    
    # Determine output path if not specified
    if args.output:
        output_path = args.output
    else:
        # Extract date from audio filename if possible
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', args.audio.name)
        date = date_match.group(1) if date_match else "unknown"
        
        # Create output filename
        clean_title = clean_for_filename(args.title)
        output_filename = f"video-{date}-{args.chapter:03d}-{clean_title}.mp4"
        
        # Default to videos directory
        project_root = Path(__file__).parent.parent
        videos_dir = project_root / "videos"
        output_path = videos_dir / output_filename
    
    # Generate the video
    success = generate_video(args.audio, args.image, output_path, args.chapter, args.title)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()