
DO NOT USE, WILL OVERWRITE GOOD DATA

import json
import sys

def remove_elements_recursive(elements, target_names):
    """
    Recursively removes elements with names matching target_names,
    and processes children of remaining elements.
    """
    filtered = []
    for elem in elements:
        if elem.get("name") not in target_names:
            # Keep this element and process its children recursively
            if "children" in elem and isinstance(elem["children"], list):
                elem["children"] = remove_elements_recursive(elem["children"], target_names)
            filtered.append(elem)
    return filtered


def rename_bones(data):
    """
    Remaps bone names to the vanilla format
    """
    bone_rename_map = {
        "b_TorsoLower": "LowerTorso",
        "b_TorsoUpper": "UpperTorso",
        "b_ArmUpperR": "UpperArmR",
        "b_ArmUpperL": "UpperArmL",
        "b_ArmLowerL": "LowerArmL",
        "b_ArmLowerR": "LowerArmR",
        "b_ItemAnchor": "ItemAnchor",
        "b_ItemAnchorL": "ItemAnchorL",
    }
    
    # Get all target names (the values we're renaming to)
    target_names = set(bone_rename_map.values())
    
    # Remove any objects with names that match the target names (recursively)
    if isinstance(data, dict) and "elements" in data:
        data["elements"] = remove_elements_recursive(data["elements"], target_names)
    
    # Convert data to JSON string
    json_str = json.dumps(data)
    
    # Replace all occurrences of bone names
    for old_name, new_name in bone_rename_map.items():
        json_str = json_str.replace(f'"{old_name}"', f'"{new_name}"')
    
    # Parse back to object
    return json.loads(json_str)


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py input.json output.json")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    data = rename_bones(data)

    # rewrite data into a patch format
    patch = {
        "file": "kemono:shapes/entity/kemono/main/kemono0.json",
        "op": "replace",
        "path": "/elements",
        "value": data.get("elements", [])
    }

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump([patch], f, indent=4)

    print(f"Wrote upper body bone name patch to {sys.argv[2]}")


if __name__ == "__main__":
    main()