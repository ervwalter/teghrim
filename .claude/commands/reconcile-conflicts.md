# Reconcile Entity Conflicts

This command helps you intelligently merge conflicting entity versions after running `pull_from_kanka.py`.

## Usage

When you have conflicts from the pull script, run this command to resolve them.

## Process

1. First, find all conflict files:
   ```bash
   find entities/ -name "*.local.md" -o -name "*.kanka.md" | sort
   ```

2. For each pair of conflict files:
   - Read the `.local.md` file (your local changes)
   - Read the `.kanka.md` file (changes from Kanka)
   - Read the current main file (e.g., `aragorn.md`)
   
3. Analyze the differences:
   - What content was added/removed in each version?
   - Are there formatting differences?
   - Are there conflicting facts or descriptions?
   - Which version has more recent/detailed information?

4. Create a merged version that:
   - Preserves all important content from both versions
   - Maintains consistent formatting
   - Resolves factual conflicts by preferring the most complete/recent information
   - Adds a note in the content if there are irreconcilable differences

5. Update the main file with the merged content

6. Clean up the conflict files:
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