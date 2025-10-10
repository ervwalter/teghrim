# Generate Images

This command generates images from session image prompts using OpenAI's DALL-E API.

## Process

1. **Run the generation script** with a 30-minute timeout:
   ```bash
   uv run python scripts/generate_images.py --dry-run
   ```
   This shows what will be generated.

2. **Generate images** (requires OPENAI_API_KEY and OPENAI_ORG_ID environment variables):
   ```bash
   uv run python scripts/generate_images.py
   ```
   Use a 1800000ms (30 minute) timeout to allow for multiple image generations.

3. **Monitor output** for:
   - Successful generations (✅)
   - Content policy violations (❌ with error about safety system or content policy)
   - Other API errors

4. **Handle content policy violations**:
   - If an image fails due to OpenAI content policy (typically overly graphic violence, gore, or horror):
     - Read the failed prompt file to understand what triggered the violation
     - Identify the problematic elements (e.g., "skinned bodies", "flayed skins", "gory wounds", "graphic violence")
     - **Generate an alternate prompt** following the guidelines in `.claude/commands/generate-image-prompts.md`:
       - Maintain the same scene/moment from the narrative
       - Preserve character descriptions (race, gender, appearance from entity files)
       - Keep the dramatic tone, lighting, and composition
       - Replace explicit gore with implied danger or aftermath
       - Reduce visceral descriptions of wounds/death
       - Tone down horror elements while keeping dramatic tension
       - Focus on action/emotion rather than graphic detail
       - Maintain the prompt structure: "Epic fantasy digital painting, [scene], [characters in parentheses], [environment], [lighting], [style]. [composition]."
       - Keep all metadata (frontmatter, Context section, Key Elements)
     - Save the edited prompt
     - Rerun the generation script

5. **Example content policy fixes**:
   - "skinned corpses" → "pale, motionless figures"
   - "flayed skin cloak" → "grotesque patchwork cloak"
   - "bones protruding from wounds" → "badly wounded"
   - "blood-soaked" → "battle-scarred"
   - "entrails visible" → "gravely injured"
   - "decapitated" → "fallen"

6. **Repeat until all images generate successfully**:
   - After editing failed prompts, run the script again
   - Continue this cycle until the script reports: "All image prompts have been generated!"

## Important Notes

- The script automatically finds prompts in `entities/notes/session-image-*.md`
- Generated images save to `images/image-YYYY-MM-DD-N.png`
- Entity links `[entity:ID|text]` are automatically cleaned from prompts
- Keep the dramatic tone and fantasy elements - just reduce graphic violence/gore
- Preserve character descriptions, lighting, composition, and artistic style notes
- Focus on the emotional/dramatic impact rather than visceral details

## Expected Workflow

```
Run generate_images.py
  ↓
Check output
  ↓
If failures → Edit problematic prompts → Rerun
  ↓
If all succeed → Done!
```

## Bash Command Template

```bash
uv run python scripts/generate_images.py
```

Timeout: 1800000ms (30 minutes)
