#!/usr/bin/env python3
"""
Generate images from prompt files using OpenAI's DALL-E API.
Preserves the exact image generation logic from the original module.
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI SDK not installed. Run: pip install openai")
    sys.exit(1)


def generate_image_from_prompt(client: OpenAI, prompt: str) -> Optional[bytes]:
    """
    Generate an image using OpenAI's image generation API.
    
    Args:
        client: OpenAI client instance
        prompt: Text prompt for image generation
        
    Returns:
        Image bytes if successful, None if failed
    """
    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1536x1024"  # 3:2 landscape aspect ratio (closest to 16:9)
        )
        
        image_base64 = result.data[0].b64_json
        return base64.b64decode(image_base64)
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None


def read_prompt_file(prompt_path: Path) -> tuple:
    """
    Read prompt from file. Supports multiple formats.
    
    Expected formats:
    1. Title on first line, prompt on rest:
       The Bridge Crossing
       A massive stone bridge spans a churning river...
       
    2. Markdown with title as header:
       # The Bridge Crossing
       A massive stone bridge spans a churning river...
       
    3. JSON format:
       {"title": "The Bridge Crossing", "prompt": "A massive stone bridge..."}
    
    Returns:
        (title, prompt) or (None, prompt) if no title found
    """
    try:
        # Try JSON format first
        if prompt_path.suffix.lower() == '.json':
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('title', prompt_path.stem), data.get('prompt', '')
        
        # Read as text
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            return None, ""
        
        lines = content.split('\n')
        
        # Check for markdown header
        if lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
            prompt = '\n'.join(lines[1:]).strip()
            return title, prompt
        
        # Check if first line looks like a title (short, no punctuation at end)
        first_line = lines[0].strip()
        if len(first_line) < 100 and not first_line.endswith(('.', '!', '?')):
            title = first_line
            prompt = '\n'.join(lines[1:]).strip()
            if prompt:  # Only use as title if there's more content
                return title, prompt
        
        # No clear title, use whole content as prompt
        return None, content
        
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return None, ""


def save_metadata(image_path: Path, title: str, prompt: str, 
                 session_date: str = None, index: int = None):
    """
    Save metadata JSON file alongside the image.
    
    Args:
        image_path: Path where image was saved
        title: Image title
        prompt: The prompt used
        session_date: Optional session date
        index: Optional image index
    """
    metadata = {
        "title": title or image_path.stem,
        "prompt": prompt,
        "filename": image_path.name
    }
    
    if session_date:
        metadata["session_date"] = session_date
    if index is not None:
        metadata["index"] = index
    
    metadata_path = image_path.with_suffix('.json')
    
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  Saved metadata: {metadata_path}")
    except Exception as e:
        print(f"  Warning: Could not save metadata: {e}")


def extract_session_info(filename: str) -> tuple:
    """
    Extract session date and index from filename if present.
    
    Expected patterns:
    - image-key-events.YYYY-MM-DD-N.txt
    - YYYY-MM-DD-N.txt
    - session-YYYY-MM-DD-image-N.txt
    
    Returns:
        (session_date, index) or (None, None)
    """
    import re
    
    # Try different patterns
    patterns = [
        r'(\d{4}-\d{2}-\d{2})-(\d+)',  # YYYY-MM-DD-N
        r'(\d{4}-\d{2}-\d{2}).*?(\d+)',  # YYYY-MM-DD...N
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1), int(match.group(2))
    
    return None, None


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from prompt files using OpenAI DALL-E",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Prompt file formats:
-------------------
1. Simple text with title on first line:
   The Bridge Crossing
   A massive stone bridge spans a churning river...

2. Markdown format:
   # The Bridge Crossing
   A massive stone bridge spans a churning river...

3. JSON format:
   {"title": "The Bridge Crossing", "prompt": "A massive stone bridge..."}

Output files:
- Image: title.png or specified output path
- Metadata: title.json (saved alongside image)
        """
    )
    parser.add_argument("prompt_file", help="Path to prompt file")
    parser.add_argument("-o", "--output", help="Output image path (default: based on title)")
    parser.add_argument("-t", "--title", help="Override image title")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--org-id", help="OpenAI organization ID (or set OPENAI_ORG_ID env var)")
    
    args = parser.parse_args()
    
    # Get API credentials
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required")
        print("Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    org_id = args.org_id or os.environ.get("OPENAI_ORG_ID")
    if not org_id:
        print("Error: OpenAI organization ID required")
        print("Set OPENAI_ORG_ID environment variable or use --org-id")
        sys.exit(1)
    
    # Read prompt file
    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}")
        sys.exit(1)
    
    # Extract prompt and title
    file_title, prompt_text = read_prompt_file(prompt_path)
    
    if not prompt_text:
        print("Error: No prompt text found in file")
        sys.exit(1)
    
    # Use provided title or extracted title or filename
    title = args.title or file_title or prompt_path.stem
    
    # Extract session info from filename if present
    session_date, index = extract_session_info(prompt_path.name)
    
    print(f"Title: {title}")
    print(f"Prompt: {prompt_text[:100]}..." if len(prompt_text) > 100 else f"Prompt: {prompt_text}")
    if session_date:
        print(f"Session: {session_date}, Image #{index}")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Clean title for filename
        clean_title = title.replace('/', '-').replace('\\', '-').replace(':', '-')
        clean_title = clean_title.replace('"', '').replace('*', '').replace('?', '')
        clean_title = clean_title.replace('<', '').replace('>', '').replace('|', '')
        
        # If we have session info, use the original naming convention
        if session_date and index is not None:
            filename = f"image-key-events.{session_date}-{index}a.png"
        else:
            filename = f"{clean_title}.png"
            
        output_path = prompt_path.parent / filename
    
    # Initialize client and generate
    print("\nGenerating image...")
    try:
        client = OpenAI(api_key=api_key, organization=org_id)
        image_bytes = generate_image_from_prompt(client, prompt_text)
        
        if image_bytes:
            # Save image
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Image saved: {output_path}")
            
            # Save metadata
            save_metadata(output_path, title, prompt_text, session_date, index)
            
            sys.exit(0)
        else:
            print("Failed to generate image")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()