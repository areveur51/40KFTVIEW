# Edges Data Files

## Active Edges
**File**: `edges.json`
- Contains all active edges displayed in the visualization
- Currently: 235 edges

## Commented/Disabled Edges
**File**: `edges_keyword_circular_commented.json`
- Contains keyword-to-keyword circular edges that have been commented out
- These edges form a circular connection between keyword nodes
- Currently: 16 edges

### Commented Keyword Circular Edges:
1. kw-COVID → kw-VirusOrElection
2. kw-NCSWIC → kw-COVID
3. kw-COVID → kw-NewsUnlocksMap
4. kw-NewsUnlocksMap → kw-NOSUCHAGENCY
5. kw-NOSUCHAGENCY → kw-PanicInDC
6. kw-PanicInDC → kw-MathematicallyImpossible
7. kw-MathematicallyImpossible → kw-PATRIOTS
8. kw-PATRIOTS → kw-QANON
9. kw-QANON → kw-FISA
10. kw-FISA → kw-SESSIONS
11. kw-SESSIONS → kw-SNOWDEN
12. kw-SNOWDEN → kw-TheGreatAwakening
13. kw-TheGreatAwakening → kw-USMIL
14. kw-USMIL → kw-VirusOrElection
15. kw-VirusOrElection → kw-WWG1WGA
16. kw-WWG1WGA → kw-RussiaHoax

## To Re-enable Commented Edges

To restore the keyword circular edges:
```bash
python3 << 'SCRIPT'
import json

# Load both files
with open('data/edges.json', 'r') as f:
    active = json.load(f)
with open('data/edges_keyword_circular_commented.json', 'r') as f:
    commented = json.load(f)

# Merge them
all_edges = active + commented

# Save
with open('data/edges.json', 'w') as f:
    json.dump(all_edges, f, indent=2)

print(f"✓ Restored {len(commented)} edges. Total: {len(all_edges)}")
SCRIPT
```
