#!/usr/bin/env python3
"""
Generate images from prompt files using OpenAI's DALL-E API.
Works with the new entity-based prompt system.
"""

import os
import sys
import json
import base64
import argparse
import re
from pathlib import Path
from typing import Optional, Tuple, List

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI SDK not installed. Run: pip install openai")
    sys.exit(1)


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


def read_prompt_file(prompt_path: Path) -> Tuple[Optional[str], str]:
    """
    Read prompt from markdown file with code block format.
    
    Expected format:
       # Scene Title
       ## Prompt
       ```
       The actual prompt text...
       ```
    
    Returns:
        (title, prompt) or (None, prompt) if no title found
    """
    try:
        # Read file content
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return None, ""
        
        # Extract prompt from code block (with or without language identifier)
        code_block_match = re.search(r'```(?:prompt)?\n(.*?)\n```', content, re.DOTALL)
        if not code_block_match:
            print("Error: No code block found in prompt file")
            return None, ""
            
        prompt_text = code_block_match.group(1).strip()
        
        # Extract title from markdown header
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Extract from filename if it's a session-image file
            if 'session-image' in prompt_path.name:
                # Format: session-image-YYYY-MM-DD-N.md
                match = re.search(r'session-image-(\d{4}-\d{2}-\d{2})-(\d+)', prompt_path.name)
                if match:
                    date, num = match.groups()
                    title = f"Session {date} - Image {num}"
                else:
                    title = prompt_path.stem
            else:
                title = prompt_path.stem
        
        # Clean entity mentions from the prompt
        prompt_text = clean_entity_mentions(prompt_text)
        return title, prompt_text
        
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return None, ""




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


def find_prompts_needing_generation() -> List[Tuple[Path, Path]]:
    """
    Find all prompt files that don't have corresponding generated images.
    
    Returns:
        List of (prompt_path, expected_image_path) tuples
    """
    # Get project root
    project_root = Path(__file__).parent.parent
    entities_dir = project_root / "entities" / "notes"
    images_dir = project_root / "images"
    
    # Find all session-image prompt files
    prompt_files = sorted(entities_dir.glob("session-image-*.md"))
    
    prompts_to_generate = []
    
    for prompt_path in prompt_files:
        # Extract date and number from filename
        match = re.search(r'session-image-(\d{4}-\d{2}-\d{2})-(\d+)', prompt_path.name)
        if match:
            date, num = match.groups()
            # Expected image filename
            image_filename = f"image-{date}-{num}.png"
            image_path = images_dir / image_filename
            
            # Add to list if image doesn't exist
            if not image_path.exists():
                prompts_to_generate.append((prompt_path, image_path))
    
    return prompts_to_generate


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from prompt files using OpenAI DALL-E",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script automatically finds session image prompts that need generation.

Looks for: entities/notes/session-image-YYYY-MM-DD-N.md
Generates: images/image-YYYY-MM-DD-N.png

Entity mentions [entity:ID|text] are automatically cleaned from prompts.
        """
    )
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--org-id", help="OpenAI organization ID (or set OPENAI_ORG_ID env var)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")
    
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
    
    # Find prompts that need generation
    prompts_to_generate = find_prompts_needing_generation()
    
    if not prompts_to_generate:
        print("All image prompts have been generated!")
        sys.exit(0)
    
    print(f"Found {len(prompts_to_generate)} image(s) to generate:")
    for prompt_path, image_path in prompts_to_generate:
        print(f"  {prompt_path.name} -> {image_path.name}")
    
    if args.dry_run:
        print("\nDry run - no images generated")
        sys.exit(0)
    
    # Initialize client
    try:
        # Set organization via environment variable if needed
        if org_id:
            os.environ['OPENAI_ORG_ID'] = org_id
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        sys.exit(1)
    
    # Process each prompt
    success_count = 0
    for prompt_path, expected_image_path in prompts_to_generate:
        print(f"\n{'='*60}")
        print(f"Processing: {prompt_path.name}")
        
        # Extract prompt and title
        title, prompt_text = read_prompt_file(prompt_path)
        
        if not prompt_text:
            print(f"  ⚠️  No prompt text found, skipping")
            continue
        
        # Extract session info
        session_date, index = extract_session_info(prompt_path.name)
        
        print(f"  Title: {title}")
        print(f"  Prompt: {prompt_text[:100]}..." if len(prompt_text) > 100 else f"  Prompt: {prompt_text}")
        
        # Generate image
        print("  Generating image...")
        try:
            image_bytes = generate_image_from_prompt(client, prompt_text)
            
            if image_bytes:
                # Save image
                expected_image_path.parent.mkdir(parents=True, exist_ok=True)
                with open(expected_image_path, "wb") as f:
                    f.write(image_bytes)
                print(f"  ✅ Image saved: {expected_image_path}")
                success_count += 1
            else:
                print(f"  ❌ Failed to generate image")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Generated {success_count}/{len(prompts_to_generate)} images successfully")
    sys.exit(0 if success_count == len(prompts_to_generate) else 1)


if __name__ == "__main__":
    main()