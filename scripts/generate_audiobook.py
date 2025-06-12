#!/usr/bin/env python3
"""
Generate audiobook MP3 from a narrative text file using ElevenLabs text-to-speech.
Preserves the exact logic from the original audiobook generation module.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List

try:
    from elevenlabs import Voice, VoiceSettings
    from elevenlabs.client import ElevenLabs
except ImportError:
    print("Error: ElevenLabs SDK not installed. Run: pip install elevenlabs")
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
    
    # Remove all markdown headers (we'll add our own chapter announcement)
    text = re.sub(r'^#{1,6}\s+.*$', '', content, flags=re.MULTILINE)
    
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
            # Multiple chunks - combine them
            print(f"  Combining {len(audio_buffers)} audio chunks...")
            combined_audio = b''.join(audio_buffers)
            with open(output_path, "wb") as f:
                f.write(combined_audio)
            
        print(f"  ✅ Audiobook created: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving audiobook: {e}")
        return False


def extract_chapter_info(narrative_path: Path) -> tuple:
    """
    Extract chapter number and title from narrative file.
    
    Expected formats:
    - First line: # Chapter N: Title
    - Filename: contains chapter number
    
    Returns:
        (chapter_num, title) or (None, None) if not found
    """
    # Try to read first line for chapter info
    try:
        with open(narrative_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            
        # Match "# Chapter N: Title" format
        match = re.match(r'^#\s*Chapter\s+(\d+):\s*(.+)', first_line, re.IGNORECASE)
        if match:
            return int(match.group(1)), match.group(2).strip()
            
        # Match "# N. Title" format
        match = re.match(r'^#\s*(\d+)\.\s*(.+)', first_line)
        if match:
            return int(match.group(1)), match.group(2).strip()
    except:
        pass
    
    # Try to extract from filename
    filename = narrative_path.stem
    
    # Match "chapter-N-title" format
    match = re.match(r'chapter[_-](\d+)[_-](.+)', filename, re.IGNORECASE)
    if match:
        title = match.group(2).replace('-', ' ').replace('_', ' ').title()
        return int(match.group(1)), title
    
    # Match "N-title" format
    match = re.match(r'^(\d+)[_-](.+)', filename)
    if match:
        title = match.group(2).replace('-', ' ').replace('_', ' ').title()
        return int(match.group(1)), title
    
    return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Generate audiobook MP3 from narrative text file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Expected narrative format:
-------------------------
# Chapter 15: The Bridge and the Bloodline

The morning mist clung to the Rothehurst River as the party crested...
[narrative continues]

Output filename will be: "NNN - Chapter Title.mp3" where NNN is the 
zero-padded chapter number (e.g., "015 - The Bridge and the Bloodline.mp3")
        """
    )
    parser.add_argument("narrative_file", help="Path to narrative text file")
    parser.add_argument("-o", "--output", help="Output MP3 path (default: auto-generated)")
    parser.add_argument("-c", "--chapter", type=int, help="Override chapter number")
    parser.add_argument("-t", "--title", help="Override chapter title")
    parser.add_argument("--api-key", help="ElevenLabs API key (or set ELEVEN_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        print("Error: ElevenLabs API key required")
        print("Set ELEVEN_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Read narrative file
    narrative_path = Path(args.narrative_file)
    if not narrative_path.exists():
        print(f"Error: Narrative file not found: {narrative_path}")
        sys.exit(1)
    
    try:
        with open(narrative_path, "r", encoding="utf-8") as f:
            narrative_content = f.read()
    except Exception as e:
        print(f"Error reading narrative file: {e}")
        sys.exit(1)
    
    # Extract or use provided chapter info
    if args.chapter and args.title:
        chapter_num = args.chapter
        title = args.title
    else:
        detected_num, detected_title = extract_chapter_info(narrative_path)
        chapter_num = args.chapter or detected_num
        title = args.title or detected_title
        
        if not chapter_num:
            print("Error: Could not determine chapter number")
            print("Use --chapter to specify or ensure file follows expected format")
            sys.exit(1)
            
        if not title:
            # Use filename as fallback title
            title = narrative_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    print(f"Chapter {chapter_num}: {title}")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Format: "NNN - Title.mp3"
        clean_title = clean_title_for_filename(title)
        output_filename = f"{chapter_num:03d} - {clean_title}.mp3"
        output_path = narrative_path.parent / output_filename
    
    # Initialize client and generate
    try:
        client = ElevenLabs(api_key=api_key)
        success = generate_audiobook(client, narrative_content, output_path, 
                                   chapter_num, title)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()