#!/usr/bin/env python3
"""
Generate podcast MP3 from a script file using ElevenLabs text-to-speech.
Takes a script file with HOST/GUEST dialogue format as input.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    from elevenlabs import Voice, VoiceSettings
    from elevenlabs.client import ElevenLabs
except ImportError:
    print("Error: ElevenLabs SDK not installed. Run: pip install elevenlabs")
    sys.exit(1)

# Voice IDs for podcast generation
HOST_VOICE_ID = "zGjIP4SZlMnY9m93k97r"
GUEST_VOICE_ID = "hmMWXCj9K7N5mCPcRkfC"

# ElevenLabs API settings
VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0,
    use_speaker_boost=True,
    speed=1.05
)
MODEL_ID = "eleven_multilingual_v2"


def parse_podcast_script(script_content: str) -> List[Tuple[str, str]]:
    """
    Parse podcast script into (speaker, text) segments.
    
    Expected format:
    HOST: Welcome to our podcast!
    GUEST: Thanks for having me.
    
    Args:
        script_content: Raw script text
        
    Returns:
        List of (speaker, text) tuples
    """
    segments = []
    current_speaker = None
    current_text_lines = []

    for line in script_content.splitlines():
        line = line.strip()
        
        # Check for speaker labels
        host_match = re.match(r"^(HOST):(.*)", line, re.IGNORECASE)
        guest_match = re.match(r"^(GUEST):(.*)", line, re.IGNORECASE)
        
        if host_match or guest_match:
            # Save previous segment if exists
            if current_speaker and current_text_lines:
                segments.append((current_speaker, "\n".join(current_text_lines).strip()))
                current_text_lines = []
            
            # Start new segment
            if host_match:
                current_speaker = "HOST"
                text_after = host_match.group(2).strip()
            else:
                current_speaker = "GUEST" 
                text_after = guest_match.group(2).strip()
            
            if text_after:
                current_text_lines.append(text_after)
                
        elif current_speaker and line:
            # Continuation of current speaker
            current_text_lines.append(line)
    
    # Don't forget last segment
    if current_speaker and current_text_lines:
        segments.append((current_speaker, "\n".join(current_text_lines).strip()))
    
    return [(s, t) for s, t in segments if t]  # Filter out empty segments


def generate_podcast(client: ElevenLabs, segments: List[Tuple[str, str]], 
                    output_path: Path) -> bool:
    """
    Generate podcast MP3 using request stitching for smooth transitions.
    
    Args:
        client: ElevenLabs client
        segments: List of (speaker, text) tuples
        output_path: Path for output MP3
        
    Returns:
        True if successful
    """
    if not segments:
        print("No valid segments found in script")
        return False
    
    audio_buffers = []
    request_ids = []
    
    print(f"Generating {len(segments)} audio segments...")
    
    for i, (speaker, text) in enumerate(segments):
        voice_id = HOST_VOICE_ID if speaker == "HOST" else GUEST_VOICE_ID
        preview = text[:60].replace('\n', ' ') + "..." if len(text) > 60 else text
        print(f"  [{i+1}/{len(segments)}] {speaker}: {preview}")
        
        try:
            # Use request stitching for consistency
            with client.text_to_speech.with_raw_response.convert(
                text=text,
                voice_id=voice_id,
                voice_settings=VOICE_SETTINGS,
                model_id=MODEL_ID,
                previous_request_ids=request_ids[-3:]  # API limit
            ) as response:
                # Track request ID for stitching
                request_id = response._response.headers.get("request-id")
                if request_id:
                    request_ids.append(request_id)
                
                # Collect audio data
                audio_data = b''.join(chunk for chunk in response.data)
                audio_buffers.append(audio_data)
                
        except Exception as e:
            print(f"Error generating segment {i+1}: {e}")
            return False
    
    # Save combined audio
    try:
        print(f"\nCombining audio segments...")
        combined_audio = b''.join(audio_buffers)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(combined_audio)
            
        print(f"✅ Podcast saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving podcast: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate podcast MP3 from script file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Script Format Example:
----------------------
HOST: Welcome to today's episode about the mansion clearing.
GUEST: It was quite an adventure! The party showed up at this bridge...
HOST: Tell us about the combat.
GUEST: Well, there were these creatures called "skims"...
        """
    )
    parser.add_argument("script_file", help="Path to podcast script file")
    parser.add_argument("-o", "--output", help="Output MP3 path (default: script_name.mp3)")
    parser.add_argument("--api-key", help="ElevenLabs API key (or set ELEVEN_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        print("Error: ElevenLabs API key required")
        print("Set ELEVEN_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Read script file
    script_path = Path(args.script_file)
    if not script_path.exists():
        print(f"Error: Script file not found: {script_path}")
        sys.exit(1)
    
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
    except Exception as e:
        print(f"Error reading script file: {e}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = script_path.with_suffix(".mp3")
    
    # Parse script
    segments = parse_podcast_script(script_content)
    if not segments:
        print("Error: No valid HOST/GUEST segments found in script")
        sys.exit(1)
    
    print(f"Found {len(segments)} dialogue segments")
    
    # Initialize client and generate
    try:
        client = ElevenLabs(api_key=api_key)
        success = generate_podcast(client, segments, output_path)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()