# Process Audio Recordings

Transcribe RPG session audio files into timestamped transcripts.

## Task

Run the audio transcription script with a 10-minute timeout (audio transcription can take several minutes):
```bash
python scripts/transcribe_audio.py
```
Use timeout: 600000 when running this command.

The script will automatically:
- Find audio files in the `session-recordings/` directory
- Check for existing transcripts
- Group files by session date
- Create timestamped, speaker-labeled transcripts
- Save results to the `transcripts/` directory

## Report

After the script completes, report:
- Which sessions were successfully transcribed
- Path to each new transcript file created
- Any errors or issues encountered

Execute this task now.