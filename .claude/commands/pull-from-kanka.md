# Pull from Kanka

This command pulls the latest entity data from Kanka and automatically reconciles any conflicts that arise.

## Usage

Run this command to sync your local entities with Kanka, automatically handling any merge conflicts.

## Process

1. First, run the pull script to fetch latest data from Kanka:
   ```bash
   python scripts/pull_from_kanka.py
   ```

2. Then, find all conflict files that may have been created:
   ```bash
   find entities/ -name "*.local.md" -o -name "*.kanka.md" | sort
   ```

3. For each pair of conflict files:
   - Read the `.local.md` file (your local changes)
   - Read the `.kanka.md` file (changes from Kanka)
   - Read the current main file (e.g., `aragorn.md`)
   
4. Analyze the differences:
   - What content was added/removed in each version?
   - Are there formatting differences?
   - Are there conflicting facts or descriptions?
   - Which version has more recent/detailed information?
   - If no meaningful differences exist, prefer the Kanka version

5. Decide on the resolution:
   - If meaningful differences exist, create a merged version that:
     - Preserves all important content from both versions
     - Maintains consistent formatting
     - Resolves factual conflicts by preferring the most complete/recent information
     - Adds a note in the content if there are irreconcilable differences
   - If no meaningful differences exist, use the Kanka version as-is

6. Update the main file:
   - If merging: Write the merged content to the main file
   - If no changes needed: Copy the Kanka version to ensure authoritative timestamps:
     ```bash
     cp <entity>.kanka.md <entity>.md
     ```

7. Clean up the conflict files:
   ```bash
   rm <entity>.local.md <entity>.kanka.md
   ```

## Example Reconciliation

If you find conflicts for Aragorn:

**Local version** might have:
- Added details about his time as Strider
- Local campaign-specific events
- GM notes about future plot points

**Kanka version** might have:
- Updated stats or attributes  
- New relationships added by other GMs
- Formatting improvements

**Merged version** should:
- Include the Strider details AND the updated stats
- Preserve both sets of relationships
- Keep GM notes if they don't conflict
- Use the better formatting

## Important Notes

- Always preserve the frontmatter from the Kanka version (it has the latest timestamps)
- If posts have conflicts, handle them the same way
- Keep campaign-specific details that might not be in the "official" Kanka version
- When in doubt, preserve both pieces of information with clear attribution

## Special Case: No Merge Needed

Sometimes after analyzing the conflicts, you might determine that:
- The versions are essentially the same
- The differences are only in timestamps or minor formatting
- No actual content conflicts exist

In these cases:
1. **Use the Kanka version** by copying it over the main file:
   ```bash
   cp <entity>.kanka.md <entity>.md
   ```
2. Delete the conflict files as usual
3. This ensures you have the authoritative version from Kanka with correct timestamps

Using the Kanka version when no merge is needed:
- Avoids unnecessary pushes back to Kanka
- Ensures you have the latest timestamps and metadata
- Maintains consistency with the remote database
- Prevents sync loops where unchanged content gets pushed back and forth