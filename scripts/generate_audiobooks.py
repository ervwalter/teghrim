#!/usr/bin/env python3
"""
Generate audiobook MP3 from narrative text files using ElevenLabs text-to-speech.
Works with the new entity-based narrative system.
"""

import os
import sys
import re
import io
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from elevenlabs import Voice, VoiceSettings
    from elevenlabs.client import ElevenLabs
except ImportError:
    print("Error: ElevenLabs SDK not installed. Run: pip install elevenlabs")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub not installed. Run: pip install pydub")
    print("Note: You may also need ffmpeg installed on your system")
    sys.exit(1)

# Voice ID for audiobook narration
NARRATOR_VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"

# ElevenLabs API settings
VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0,
    use_speaker_boost=True,
    speed=1.05
)
MODEL_ID = "eleven_multilingual_v2"


def clean_entity_mentions(text: str) -> str:
    """
    Remove entity mentions [entity:ID|text] and leave just the text.
    
    Args:
        text: Text containing entity mentions
        
    Returns:
        Cleaned text without entity markup
    """
    # Pattern for [entity:ID|text] - keep the text part
    text = re.sub(r'\[entity:\d+\|([^\]]+)\]', r'\1', text)
    # Pattern for [entity:ID] - remove entirely since there's no display text
    text = re.sub(r'\[entity:\d+\]', '', text)
    return text


def clean_title_for_filename(title: str) -> str:
    """
    Clean a title to be safe for use in a filename.
    
    Args:
        title: Raw title text
        
    Returns:
        Cleaned title safe for filenames
    """
    # Remove invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Remove any markdown formatting
    title = title.replace('#', '').strip()
    # Limit length to avoid filesystem issues
    if len(title) > 100:
        title = title[:100].rstrip()
    return title


def prepare_text_for_tts(content: str, chapter_num: int, title: str) -> str:
    """
    Prepare narrative text for text-to-speech conversion.
    
    Args:
        content: Raw narrative content
        chapter_num: Chapter number
        title: Chapter title
        
    Returns:
        Cleaned text suitable for TTS with chapter announcement
    """
    # Start with chapter announcement
    chapter_announcement = f"Chapter {chapter_num}: {title}...\n\n"
    
    # Remove YAML frontmatter if present
    if content.startswith('---'):
        # Find the end of frontmatter (second ---)
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # Use only the content after frontmatter
            text = parts[2].strip()
        else:
            text = content
    else:
        text = content
    
    # Clean entity mentions
    text = clean_entity_mentions(text)
    
    # Remove all markdown headers (we'll add our own chapter announcement)
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    
    # Convert markdown emphasis to plain text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'_(.+?)_', r'\1', text)  # Italic
    
    # Remove markdown links but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Clean up multiple blank lines
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Trim whitespace and prepend chapter announcement
    text = chapter_announcement + text.strip()
    
    return text


def split_text_into_chunks(text: str, max_chunk_size: int = 3000) -> List[str]:
    """
    Split text into chunks at sentence boundaries.
    Updated to use 3000 character chunks as per original.
    
    Args:
        text: Text to split
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    sentences = text.replace('\n\n', '\n<PARA>\n').split('.')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Add period back unless it's a paragraph marker
        if not sentence.endswith('<PARA>'):
            sentence += '.'
        else:
            sentence = sentence.replace('<PARA>', '\n\n')
            
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += (' ' if current_chunk else '') + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


def normalize_audio(input_path: Path, output_path: Path) -> bool:
    """
    Normalize audio using ffmpeg to fix volume dropoff issues.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path for the normalized output
        
    Returns:
        bool: True if successful
    """
    try:
        # Check if ffmpeg is available
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=False)
        if result.returncode != 0:
            print("  Warning: ffmpeg not found. Audio normalization skipped.")
            print("  Install ffmpeg to enable audio normalization: apt-get install ffmpeg")
            return False
        
        # Create temporary file for normalization
        temp_path = output_path.with_suffix('.temp.mp3')
        
        # Run ffmpeg normalization using compressor + loudnorm
        # This approach handles the ElevenLabs volume dropoff issue better
        # acompressor: Compress dynamic range to prevent gradual volume decrease
        #   - threshold=-20dB: Compression threshold
        #   - ratio=4: Compression ratio (4:1)
        #   - attack=5: Attack time in ms
        #   - release=50: Release time in ms
        # loudnorm: EBU R128 loudness normalization for consistent overall level
        #   - I=-23: Target integrated loudness (lowered from -20 for quieter output)
        #   - LRA=7: Loudness range
        #   - TP=-2: True peak
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-af", "acompressor=threshold=-20dB:ratio=4:attack=5:release=50,loudnorm=I=-23:LRA=7:TP=-2",
            "-codec:a", "libmp3lame", "-b:a", "192k",
            "-y",  # Overwrite output
            str(temp_path)
        ]
        
        print("  Normalizing audio levels...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Replace original with normalized version
            temp_path.rename(output_path)
            return True
        else:
            print(f"  Warning: Audio normalization failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Warning: Audio normalization error: {e}")
        return False


def generate_audiobook(client: ElevenLabs, narrative_content: str, 
                      output_path: Path, chapter_num: int, title: str) -> bool:
    """
    Generate an audiobook MP3 from narrative content.
    
    Args:
        client: ElevenLabs client
        narrative_content: Narrative text content
        output_path: Path for the output MP3
        chapter_num: Chapter number
        title: Chapter title
        
    Returns:
        bool: True if successful
    """
    print(f"Generating audiobook for Chapter {chapter_num}: {title}")
    
    # Prepare text for TTS with chapter announcement
    tts_text = prepare_text_for_tts(narrative_content, chapter_num, title)
    if not tts_text.strip():
        print(f"No text content found for Chapter {chapter_num}")
        return False
    
    # Split into chunks if text is too long
    chunks = split_text_into_chunks(tts_text, max_chunk_size=3000)
    audio_buffers = []
    request_ids = []
    
    print(f"  Converting text to speech ({len(tts_text)} characters in {len(chunks)} chunks)...")
    
    for i, chunk in enumerate(chunks):
        try:
            if len(chunks) > 1:
                print(f"  Processing chunk {i+1}/{len(chunks)} ({len(chunk)} characters)...")
            
            # Use with_raw_response to get headers for request stitching
            with client.text_to_speech.with_raw_response.convert(
                text=chunk,
                voice_id=NARRATOR_VOICE_ID,
                voice_settings=VOICE_SETTINGS,
                model_id=MODEL_ID,
                previous_request_ids=request_ids[-3:]  # Pass only last 3 request IDs (API limit)
            ) as response:
                # Get the request ID for this generation
                request_id = response._response.headers.get("request-id")
                if request_id:
                    request_ids.append(request_id)
                
                # Collect the audio data
                audio_data = b''.join(chunk for chunk in response.data)
                audio_buffers.append(audio_data)
            
        except Exception as conversion_error:
            print(f"  Error converting chunk {i+1} to audio: {conversion_error}")
            return False
    
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Combine all audio buffers into a single file
        if len(audio_buffers) == 1:
            # Single chunk - write directly
            with open(output_path, "wb") as f:
                f.write(audio_buffers[0])
        else:
            # Multiple chunks - combine them properly using pydub
            print(f"  Combining {len(audio_buffers)} audio chunks...")
            
            # Convert each MP3 chunk to AudioSegment and combine
            combined_audio = AudioSegment.empty()
            for i, audio_buffer in enumerate(audio_buffers):
                try:
                    # Load MP3 data into AudioSegment
                    audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_buffer))
                    combined_audio += audio_segment
                except Exception as e:
                    print(f"    Warning: Error processing chunk {i+1}: {e}")
            
            # Export the combined audio as MP3
            combined_audio.export(output_path, format="mp3", bitrate="192k")
        
        # Normalize the audio to fix volume dropoff
        normalized = normalize_audio(output_path, output_path)
        if normalized:
            print(f"  ✅ Audiobook created and normalized: {output_path}")
        else:
            print(f"  ✅ Audiobook created: {output_path}")
            print("     (Audio normalization skipped - install ffmpeg for better quality)")
        
        return True
        
    except Exception as e:
        print(f"Error saving audiobook: {e}")
        return False


def extract_chapter_info(narrative_path: Path) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract chapter number and title from narrative file.
    
    Expected formats:
    - Markdown heading: # Chapter N - Title
    - Frontmatter: name: 01 - The Bridge and the Bloodline
    - Filename: session-narrative-YYYY-MM-DD.md
    
    Returns:
        (chapter_num, title) or (None, None) if not found
    """
    # Try to read the file content for chapter info
    try:
        with open(narrative_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match "# Chapter N - Title" format
        match = re.search(r'^#\s*Chapter\s+(\d+)\s*[-:]\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if match:
            return int(match.group(1)), match.group(2).strip()
            
        # Try to find from frontmatter name field
        # name: 01 - The Bridge and the Bloodline
        match = re.search(r'^name:\s*(\d+)\s*-\s*(.+)$', content, re.MULTILINE)
        if match:
            return int(match.group(1)), match.group(2).strip()
    except:
        pass
    
    # If we couldn't find chapter info in the file content
    return None, None


def find_narratives_needing_audio() -> List[Tuple[Path, int, str, str]]:
    """
    Find all narrative files that don't have corresponding audiobooks.
    
    Returns:
        List of (narrative_path, chapter_num, title, date) tuples
    """
    # Get project root
    project_root = Path(__file__).parent.parent
    narratives_dir = project_root / "entities" / "journals"
    audiobooks_dir = project_root / "audiobooks"
    
    # Find all session-narrative files
    narrative_files = sorted(narratives_dir.glob("session-narrative-*.md"))
    
    narratives_to_generate = []
    
    for narrative_path in narrative_files:
        # Extract date from filename
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', narrative_path.name)
        date = date_match.group(1) if date_match else ""
        
        # Extract chapter info from the file
        chapter_num, title = extract_chapter_info(narrative_path)
        
        if chapter_num and title and date:
            # Expected audiobook filename
            clean_title = clean_title_for_filename(title)
            audio_filename = f"audiobook-{date}-{chapter_num:03d}-{clean_title}.mp3"
            audio_path = audiobooks_dir / audio_filename
            
            # Add to list if audiobook doesn't exist
            if not audio_path.exists():
                narratives_to_generate.append((narrative_path, chapter_num, title, date))
    
    return narratives_to_generate


def main():
    parser = argparse.ArgumentParser(
        description="Generate audiobook MP3s from narrative text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script automatically finds session narratives that need audiobook generation.

Looks for: entities/journals/session-narrative-YYYY-MM-DD.md
Generates: audiobooks/audiobook-YYYY-MM-DD-001-Chapter Title.mp3

Entity mentions [entity:ID|text] are automatically cleaned from narratives.
        """
    )
    parser.add_argument("--api-key", help="ElevenLabs API key (or set ELEVEN_API_KEY env var)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        print("Error: ElevenLabs API key required")
        print("Set ELEVEN_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Find narratives that need audio generation
    narratives_to_generate = find_narratives_needing_audio()
    
    if not narratives_to_generate:
        print("All narratives have audiobooks!")
        sys.exit(0)
    
    print(f"Found {len(narratives_to_generate)} audiobook(s) to generate:")
    for narrative_path, chapter_num, title, date in narratives_to_generate:
        print(f"  Chapter {chapter_num}: {title} ({narrative_path.name})")
    
    if args.dry_run:
        print("\nDry run - no audiobooks generated")
        print("\n" + "="*60)
        print("TEXT PREVIEW (first narrative):")
        print("="*60)
        
        # Show a preview of the first narrative's processed text
        if narratives_to_generate:
            first_narrative = narratives_to_generate[0]
            narrative_path, chapter_num, title, date = first_narrative
            try:
                with open(narrative_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Process the text as it would be for TTS
                processed_text = prepare_text_for_tts(content, chapter_num, title)
                # Show first 500 characters
                preview_length = 500
                if len(processed_text) > preview_length:
                    print(f"{processed_text[:preview_length]}...")
                    print(f"\n[Truncated - full text is {len(processed_text)} characters]")
                else:
                    print(processed_text)
            except Exception as e:
                print(f"Error reading narrative: {e}")
        
        print("\n" + "="*60)
        sys.exit(0)
    
    # Initialize client
    try:
        client = ElevenLabs(api_key=api_key)
    except Exception as e:
        print(f"Error initializing ElevenLabs client: {e}")
        sys.exit(1)
    
    # Process each narrative
    success_count = 0
    for narrative_path, chapter_num, title, date in narratives_to_generate:
        print(f"\n{'='*60}")
        print(f"Processing: Chapter {chapter_num} - {title}")
        
        try:
            # Read narrative content
            with open(narrative_path, "r", encoding="utf-8") as f:
                narrative_content = f.read()
        except Exception as e:
            print(f"  ❌ Error reading narrative: {e}")
            continue
        
        # Determine output path
        project_root = Path(__file__).parent.parent
        audiobooks_dir = project_root / "audiobooks"
        audiobooks_dir.mkdir(exist_ok=True)
        
        clean_title_text = clean_title_for_filename(title)
        output_filename = f"audiobook-{date}-{chapter_num:03d}-{clean_title_text}.mp3"
        output_path = audiobooks_dir / output_filename
        
        # Generate audiobook
        try:
            success = generate_audiobook(client, narrative_content, output_path, 
                                       chapter_num, title)
            if success:
                success_count += 1
            else:
                print(f"  ❌ Failed to generate audiobook")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Generated {success_count}/{len(narratives_to_generate)} audiobooks successfully")
    sys.exit(0 if success_count == len(narratives_to_generate) else 1)


if __name__ == "__main__":
    main()