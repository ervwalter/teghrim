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

### 2.2 Get chapter info and image URL from the session narrative
Read the file `entities/journals/session-narrative-YYYY-MM-DD.md` and extract:
- From frontmatter:
  - `name` field: look for pattern "NN - Title" where NN is chapter number
  - `image` field: contains the Kanka CDN URL
- Or from content: look for "# Chapter N - Title" or "# Chapter N: Title" if not in frontmatter

If the narrative doesn't have an `image` field:
1. List only images that match the session date in the `images/` folder:
   ```bash
   ls -1 images/image-YYYY-MM-DD-*.png | nl -w2 -s'. '
   ```
   Where YYYY-MM-DD is extracted from the audiobook filename
2. Show the user the numbered list and ask them to choose:
   - Display: "Available images for [chapter title] (YYYY-MM-DD):"
   - Show numbered list (1. filename1, 2. filename2, etc.)
   - Ask: "Which image should be used? You can say 'the first one', 'the second one', 'number 3', 'the last one', etc."
3. Parse user response to extract the selection:
   - "first"/"the first one" → select item 1
   - "second"/"the second one" → select item 2  
   - "third"/"the third one" → select item 3
   - "last"/"the last one" → select the final item
   - "number N"/"N" → select item N
4. Use the selected image file from the images/ folder

### 2.3 Prepare the image
If using an image URL from the narrative:
```bash
# Create a temporary file for the image
temp_image=$(mktemp /tmp/session-image-XXXXXX.png)

# Download the image using curl or wget
curl -L -o "$temp_image" "$image_url"
```

If using a local image from the images/ folder:
```bash
# Use the selected image file directly
image_file="images/selected-filename.png"  # Use the actual selected filename
```

### 2.4 Generate the video
If using a downloaded image:
```bash
python3 scripts/generate_video_from_audio.py \
  "audiobooks/audiobook-YYYY-MM-DD-NNN-Title.mp3" \
  "$temp_image" \
  --chapter CHAPTER_NUMBER \
  --title "Chapter Title"

# Clean up the temporary image
rm "$temp_image"
```

If using a local image file:
```bash
python3 scripts/generate_video_from_audio.py \
  "audiobooks/audiobook-YYYY-MM-DD-NNN-Title.mp3" \
  "$image_file" \
  --chapter CHAPTER_NUMBER \
  --title "Chapter Title"

# No cleanup needed for local files
```

## Step 3: Report results

After processing all audiobooks, report:
- How many audiobooks were found
- How many already had videos
- How many new videos were generated
- Any errors encountered

## Error handling

- If session narrative is missing: skip with warning
- If image URL is missing from narrative: prompt user to select from matching date images in images/ folder
- If no matching date images found and no image URL: skip with warning
- If user doesn't respond to image selection prompt: skip with warning
- If image download fails: skip with warning
- If selected local image file doesn't exist: skip with warning
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
  - Found image URL in session narrative
  - Downloading image...
  - Generating video...
  ✓ Created video-2025-06-13-004-The_Spore_and_the_Cure.mp4

Processing audiobook-2025-06-20-005-The_One-Eyed_Witness.mp3:
  - Found chapter info: Chapter 5 - The One-Eyed Witness
  - Found image URL in session narrative
  - Downloading image...
  - Generating video...
  ✓ Created video-2025-06-20-005-The_One-Eyed_Witness.mp4

Summary: Generated 2 new videos successfully
```