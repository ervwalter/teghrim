#!/usr/bin/env python3
"""
Simple standalone script to transcribe audio files using ElevenLabs API.
Processes audio files from ../audio/ and saves transcripts to ../transcripts/
Automatically splits files longer than 2 hours.
"""

import os
import sys
import re
import json
import time
import shutil
from typing import List, Dict, Tuple, Optional
from elevenlabs.client import ElevenLabs

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub not installed. Run: pip install pydub")
    print("Note: pydub requires ffmpeg. Install with: apt-get install ffmpeg (Linux) or brew install ffmpeg (Mac)")
    sys.exit(1)


def extract_date_from_filename(filename: str) -> Tuple[str, str]:
    """
    Extract date from filename format YYMMDD_####.mp3 and convert to YYYY-MM-DD.
    
    Returns:
        Tuple of (raw_date, formatted_date)
    """
    match = re.match(r'^(\d{6})_', os.path.basename(filename))
    if not match:
        raise ValueError(f"Could not extract date from filename: {filename}")
    
    raw_date = match.group(1)
    year = int(f"20{raw_date[0:2]}")
    month = int(raw_date[2:4])
    day = int(raw_date[4:6])
    
    return raw_date, f"{year}-{month:02d}-{day:02d}"


def group_audio_by_date(audio_dir: str) -> Dict[str, List[str]]:
    """Group audio files by session date."""
    files_by_date = {}
    
    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory {audio_dir} does not exist")
        return files_by_date
    
    for filename in os.listdir(audio_dir):
        if filename.lower().endswith('.mp3') and re.match(r'^\d{6}_\d{4}', filename):
            file_path = os.path.join(audio_dir, filename)
            try:
                _, formatted_date = extract_date_from_filename(filename)
                if formatted_date not in files_by_date:
                    files_by_date[formatted_date] = []
                files_by_date[formatted_date].append(file_path)
            except ValueError as e:
                print(f"Warning: Skipping {filename}: {str(e)}")
    
    # Sort files within each date
    for date in files_by_date:
        files_by_date[date].sort()
    
    return files_by_date


def split_long_audio_file(audio_path: str, max_duration_sec: int = 6900) -> List[str]:
    """
    Split a long audio file into segments of at most max_duration_sec.
    Default is 6900 seconds (1 hour 55 minutes) to stay under Eleven Labs 2-hour limit.
    
    Args:
        audio_path: Path to the audio file
        max_duration_sec: Maximum duration of each segment in seconds
        
    Returns:
        List of paths to the generated segment files
    """
    # Load the audio file
    try:
        audio = AudioSegment.from_mp3(audio_path)
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {str(e)}", file=sys.stderr)
        return [audio_path]  # Return the original file if there's an error
    
    # If the file is already short enough, return the original path
    duration_sec = len(audio) / 1000  # pydub duration is in milliseconds
    if duration_sec <= max_duration_sec:
        return [audio_path]
    
    # Get directory and filename parts
    base_dir = os.path.dirname(audio_path)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    file_ext = os.path.splitext(os.path.basename(audio_path))[1]
    
    # Create a backups directory
    backups_dir = os.path.join(base_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    backup_path = os.path.join(backups_dir, f"{base_name}{file_ext}")
    
    # Calculate how many segments we need
    segment_count = int(duration_sec / max_duration_sec) + 1
    segment_paths = []
    
    print(f"  File is {duration_sec/60:.1f} minutes long, splitting into {segment_count} segments...")
    
    # Split the audio into segments
    all_segments_successful = True
    for i in range(segment_count):
        start_time = i * max_duration_sec * 1000  # Convert to milliseconds
        end_time = min((i + 1) * max_duration_sec * 1000, len(audio))
        segment = audio[start_time:end_time]
        
        # Create a filename for the segment directly in the audio folder
        # Format: original_name_partXX.mp3
        segment_file = os.path.join(base_dir, f"{base_name}_part{i+1:02d}.mp3")
        
        try:
            segment.export(segment_file, format="mp3")
            segment_paths.append(segment_file)
            print(f"  Created segment {i+1}/{segment_count}: {os.path.basename(segment_file)}")
        except Exception as e:
            print(f"  Error creating segment {i+1}: {str(e)}", file=sys.stderr)
            all_segments_successful = False
    
    # If all segments were created successfully, move the original file to backups
    if all_segments_successful:
        try:
            shutil.move(audio_path, backup_path)
            print(f"  Moved original file to: {backup_path}")
        except Exception as e:
            print(f"  Warning: Could not move original file to {backup_path}: {str(e)}", file=sys.stderr)
    
    return segment_paths


def format_transcript(transcription_data, time_offset: float = 0.0) -> str:
    """
    Format the transcription with speaker labels and timestamps.
    
    Args:
        transcription_data: Raw response from ElevenLabs API
        time_offset: Cumulative time offset from previous files
        
    Returns:
        Formatted transcript with speaker labels and timestamps
    """
    if not transcription_data:
        return "*No transcription data available*"
    
    # Check for word-level data
    if not hasattr(transcription_data, 'words') or not transcription_data.words:
        # Fallback to simple text
        text = getattr(transcription_data, 'text', "No transcription text available")
        return text
    
    markdown = []
    current_speaker = None
    speaker_map = {}  # Maps speaker_id to Speaker 1, 2, 3...
    next_speaker_num = 1
    current_paragraph = []
    last_end_time = 0
    
    for word_info in transcription_data.words:
        if not hasattr(word_info, 'text'):
            continue
            
        text = getattr(word_info, 'text', '')
        speaker_id = getattr(word_info, 'speaker_id', 'unknown')
        start_time = getattr(word_info, 'start', 0)
        end_time = getattr(word_info, 'end', 0)
        
        if not text:
            continue
        
        # Map speaker_id to Speaker N
        if speaker_id not in speaker_map and speaker_id != 'unknown':
            speaker_map[speaker_id] = f"Speaker {next_speaker_num}"
            next_speaker_num += 1
        
        speaker_label = speaker_map.get(speaker_id, 'Unknown Speaker')
        
        # Check for speaker change or long pause (>1.5 seconds)
        if (current_speaker != speaker_id or 
            (current_speaker and start_time - last_end_time > 1.5)):
            
            # Add current paragraph if exists
            if current_paragraph:
                markdown.append(''.join(current_paragraph).strip() + '\n\n')
                current_paragraph = []
            
            # Add speaker label with timestamp if speaker changed
            if current_speaker != speaker_id:
                # Calculate cumulative time
                cumulative_time = time_offset + start_time
                hours, remainder = divmod(cumulative_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"[{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}]"
                
                current_paragraph.append(f"{time_str} {speaker_label}: ")
                current_speaker = speaker_id
        
        current_paragraph.append(text)
        last_end_time = end_time
    
    # Add last paragraph
    if current_paragraph:
        markdown.append(''.join(current_paragraph).strip() + '\n\n')
    
    return ''.join(markdown).replace('  ', ' ').strip()


def transcribe_file(file_path: str, api_key: str, num_speakers: int = 6, 
                   output_file: Optional[str] = None, time_offset: float = 0.0) -> Tuple[Optional[object], str, float]:
    """
    Transcribe a single audio file.
    
    Returns:
        Tuple of (transcription_object, formatted_transcript, duration)
    """
    print(f"  Transcribing {os.path.basename(file_path)}...")
    
    try:
        # Read audio file
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        # Initialize client
        client = ElevenLabs(api_key=api_key, timeout=300)
        
        # Make API request
        transcription = client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",
            language_code="eng",
            diarize=True,
            num_speakers=num_speakers,
            tag_audio_events=True
        )
        
        # Format transcript with time offset
        formatted = format_transcript(transcription, time_offset)
        
        # Get duration
        duration = 0
        if hasattr(transcription, 'words') and transcription.words:
            last_word = transcription.words[-1]
            if hasattr(last_word, 'end'):
                duration = last_word.end
        
        # Save individual file if output path provided
        if output_file and output_file != "skip_file_output":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted)
        
        return transcription, formatted, duration
        
    except Exception as e:
        error_msg = f"Error transcribing {os.path.basename(file_path)}: {str(e)}"
        print(f"  {error_msg}")
        return None, f"*{error_msg}*\n\n", 0


def process_session(date: str, audio_files: List[str], api_key: str, transcripts_dir: str) -> bool:
    """
    Process all audio files for a session and create combined transcript.
    
    Returns:
        True if successful, False otherwise
    """
    # Check for existing transcript
    output_path = os.path.join(transcripts_dir, f"{date}.md")
    if os.path.exists(output_path):
        print(f"Transcript for {date} already exists, skipping")
        return True
    
    # Create segments directory for individual pieces
    segments_dir = os.path.join(transcripts_dir, "segments", date)
    os.makedirs(segments_dir, exist_ok=True)
    
    print(f"\nProcessing session {date} with {len(audio_files)} file(s)")
    
    # Process audio files, splitting if necessary
    processed_files = []
    for file_path in audio_files:
        segment_paths = split_long_audio_file(file_path)
        processed_files.extend(segment_paths)
    
    # Process files
    transcript_parts = []
    cumulative_time = 0.0
    all_successful = True
    
    for i, file_path in enumerate(processed_files):
        file_basename = os.path.basename(file_path)
        segment_file = os.path.join(segments_dir, f"{file_basename}.md")
        
        # Check if segment already exists
        if os.path.exists(segment_file):
            print(f"  Segment for {file_basename} already exists, loading...")
            with open(segment_file, "r") as f:
                content = f.read()
            
            # Extract duration from metadata
            duration_match = re.search(r'DURATION:(\d+\.\d+)', content)
            if duration_match:
                duration = float(duration_match.group(1))
                cumulative_time += duration
            
            # Remove metadata before adding to transcript
            content = re.sub(r'DURATION:\d+\.\d+\n', '', content)
            transcript_parts.append(content)
        else:
            # Transcribe the file
            transcription_obj, formatted, duration = transcribe_file(
                file_path, api_key, output_file="skip_file_output", time_offset=cumulative_time
            )
            
            if transcription_obj is None:
                all_successful = False
                break
            
            # Save segment with metadata
            if formatted.strip():
                with open(segment_file, "w") as f:
                    f.write(f"DURATION:{duration}\n")
                    f.write(formatted)
            
            transcript_parts.append(formatted)
            cumulative_time += duration
        
        # Add separator between files
        if i < len(processed_files) - 1:
            transcript_parts.append("\n---\n\n")
    
    # Save combined transcript only if all successful
    if all_successful:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("".join(transcript_parts))
            print(f"Saved transcript to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return False
    else:
        print("Transcription incomplete due to errors")
        return False


def main():
    """Main entry point."""
    # Check for API key
    api_key = os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        print("Error: ELEVEN_API_KEY environment variable not set")
        sys.exit(1)
    
    # Set up directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # new-plan directory
    audio_dir = os.path.join(base_dir, "audio")
    transcripts_dir = os.path.join(base_dir, "transcripts")
    
    # Create transcripts directory
    os.makedirs(transcripts_dir, exist_ok=True)
    
    # Find sessions
    sessions = group_audio_by_date(audio_dir)
    if not sessions:
        print("No audio files found")
        return
    
    # Find unprocessed sessions
    unprocessed = []
    for date, files in sessions.items():
        transcript_path = os.path.join(transcripts_dir, f"{date}.md")
        if not os.path.exists(transcript_path):
            unprocessed.append((date, files))
    
    if not unprocessed:
        print("All sessions already transcribed")
        return
    
    print(f"Found {len(unprocessed)} unprocessed session(s)")
    
    # Sort unprocessed sessions by date to process chronologically
    unprocessed.sort(key=lambda x: x[0])
    
    # Process each session
    failed = []
    for date, files in unprocessed:
        if not process_session(date, files, api_key, transcripts_dir):
            failed.append(date)
    
    # Summary
    if failed:
        print(f"\nFailed to process {len(failed)} session(s): {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nSuccessfully processed all sessions")


if __name__ == "__main__":
    main()