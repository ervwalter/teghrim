# Generate Videos from Audiobooks

Find all audiobooks that don't have corresponding videos and generate them using the session images.

## Step 1: Find audiobooks needing videos

```bash
# List all audiobook files
ls audiobooks/audiobook-*.mp3

# Create videos directory if it doesn't exist
mkdir -p videos

# List existing videos to see what we already have
ls videos/video-*.mp4
```

For each audiobook file, check if a corresponding video exists. An audiobook named `audiobook-2025-06-13-004-The_Spore_and_the_Cure.mp3` would have a video named `video-2025-06-13-004-*.mp4`.

## Step 2: Process each audiobook without a video

For each audiobook that needs a video:

### 2.1 Extract the date from the audiobook filename
The audiobook filename format is: `audiobook-YYYY-MM-DD-NNN-Title.mp3`
Extract the date portion (YYYY-MM-DD) using regex or string splitting.

### 2.2 Get chapter info from the session narrative
Read the file `entities/journals/session-narrative-YYYY-MM-DD.md` and extract:
- From frontmatter `name` field: look for pattern "NN - Title" where NN is chapter number
- Or from content: look for "# Chapter N - Title" or "# Chapter N: Title"

### 2.3 Get the image URL from session summary
Read the file `entities/journals/session-summary-YYYY-MM-DD.md` and:
- Extract the YAML frontmatter
- Get the `image` field which contains the Kanka CDN URL

### 2.4 Download the image temporarily
```bash
# Create a temporary file for the image
temp_image=$(mktemp /tmp/session-image-XXXXXX.png)

# Download the image using curl or wget
curl -L -o "$temp_image" "$image_url"
```

### 2.5 Generate the video
```bash
python3 scripts/generate_video_from_audio.py \
  "audiobooks/audiobook-YYYY-MM-DD-NNN-Title.mp3" \
  "$temp_image" \
  --chapter CHAPTER_NUMBER \
  --title "Chapter Title"

# Clean up the temporary image
rm "$temp_image"
```

## Step 3: Report results

After processing all audiobooks, report:
- How many audiobooks were found
- How many already had videos
- How many new videos were generated
- Any errors encountered

## Error handling

- If session narrative is missing: skip with warning
- If session summary is missing: skip with warning
- If image URL is missing from summary: skip with warning
- If image download fails: skip with warning
- If video generation fails: report the error but continue with next audiobook

## Example execution trace

```
Found 5 audiobooks:
- audiobook-2025-05-16-001-The_Bridge_and_the_Bloodline.mp3 ✓ (video exists)
- audiobook-2025-05-23-002-Stone_Hearts_and_Fairy_Rings.mp3 ✓ (video exists)
- audiobook-2025-05-30-003-Necromancer's_Welcome.mp3 ✓ (video exists)
- audiobook-2025-06-13-004-The_Spore_and_the_Cure.mp3 ✗ (needs video)
- audiobook-2025-06-20-005-The_One-Eyed_Witness.mp3 ✗ (needs video)

Processing audiobook-2025-06-13-004-The_Spore_and_the_Cure.mp3:
  - Found chapter info: Chapter 4 - The Spore and the Cure
  - Found image URL in session summary
  - Downloading image...
  - Generating video...
  ✓ Created video-2025-06-13-004-The_Spore_and_the_Cure.mp4

Processing audiobook-2025-06-20-005-The_One-Eyed_Witness.mp3:
  - Found chapter info: Chapter 5 - The One-Eyed Witness
  - Found image URL in session summary
  - Downloading image...
  - Generating video...
  ✓ Created video-2025-06-20-005-The_One-Eyed_Witness.mp4

Summary: Generated 2 new videos successfully
```