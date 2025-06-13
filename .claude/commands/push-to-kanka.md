# Push to Kanka

This command pushes all local entity changes to Kanka.

## Usage

Run this command to push all your local entity changes to Kanka with a confirmation prompt.

## Process

Execute the push script with the --all flag:
```bash
python scripts/push_to_kanka.py --all
```

This will:
1. Find all local entities that have been modified
2. Show you a list of what will be pushed
3. Ask for confirmation before pushing
4. Update the Kanka database with your local changes
5. Update local files with any new entity IDs or timestamps returned by Kanka