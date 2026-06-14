
DO NOT USE, WILL OVERWRITE GOOD DATA


import json
import sys


# Elements that should come from seraph-faceless.json when merging
SERAPH_ELEMENTS = {
    # "LowerTorso",
    # "UpperTorso",
    # "UpperArmR",
    # "UpperArmL",
    # "LowerArmL",
    # "LowerArmR",
    # "ItemAnchor",
    # "ItemAnchorL",
}

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

def rename_bones(data):
    """
    Remaps bone names to the kemono format
    """
    
    # Convert data to JSON string
    json_str = json.dumps(data)
    
    # Replace all occurrences of bone names
    for old_name, new_name in bone_rename_map.items():
        json_str = json_str.replace(f'"{old_name}"', f'"{new_name}"')
    
    # Parse back to object
    return json.loads(json_str)


def remap_rotation(rot_x, rot_y, rot_z):
    """Remap rotation coordinates from seraph to target coordinate system."""
    return rot_y, -rot_z, rot_x


def remap_position(pos_x, pos_y, pos_z):
    """Remap position coordinates from seraph to target coordinate system."""
    return -pos_y, -pos_z, pos_x


def apply_seraph_transforms(element):
    """
    Apply coordinate transformation to seraph element data.
    Transforms rotations and positions using the remap functions.
    """
    transformed = element.copy()
    
    # Transform rotations if they exist
    if 'rotationX' in element and 'rotationY' in element and 'rotationZ' in element:
        rot_x, rot_y, rot_z = remap_rotation(
            element['rotationX'],
            element['rotationY'],
            element['rotationZ']
        )
        transformed['rotationX'] = rot_x
        transformed['rotationY'] = rot_y
        transformed['rotationZ'] = rot_z
    
    # Transform positions if they exist
    if 'offsetX' in element and 'offsetY' in element and 'offsetZ' in element:
        pos_x, pos_y, pos_z = remap_position(
            element['offsetX'],
            element['offsetY'],
            element['offsetZ']
        )
        transformed['offsetX'] = pos_x
        transformed['offsetY'] = pos_y
        transformed['offsetZ'] = pos_z
    
    return transformed


def merge_animations(seraph_file, kemono_file):
    """
    Merge animations from two sources.
    For matching animation codes and frame numbers, use elements from seraph-faceless
    for the specified bones, and use all other elements from kemono0_animations.
    """
    with open(seraph_file, 'r', encoding='utf-8') as f:
        seraph_data = json.load(f)
    
    with open(kemono_file, 'r', encoding='utf-8') as f:
        kemono_data = json.load(f)

    kemono_data = rename_bones(kemono_data)
    
    # Create a mapping of animations by code for quick lookup
    seraph_anims = {anim['code']: anim for anim in seraph_data.get('animations', [])}
    kemono_anims = {anim['code']: anim for anim in kemono_data.get('animations', [])}
    
    # Result animations
    result_anims = []
    processed_codes = set()
    
    # Process animations from both sources
    all_codes = set(seraph_anims.keys()) | set(kemono_anims.keys())
    
    for code in sorted(all_codes):
        seraph_anim = seraph_anims.get(code)
        kemono_anim = kemono_anims.get(code)
        
        if seraph_anim and kemono_anim:
            # Both have this animation - merge them
            merged_anim = merge_single_animation(seraph_anim, kemono_anim)
            result_anims.append(merged_anim)
        elif seraph_anim:
            # Only in seraph - filter to allowed elements
            filtered_anim = filter_animation(seraph_anim)
            if filtered_anim['keyframes']:  # Only add if has keyframes left
                result_anims.append(filtered_anim)
        # else:
        #     # Only in kemono - add as-is
        #     result_anims.append(kemono_anim)
        
        processed_codes.add(code)
    
    return result_anims


def filter_animation(anim):
    """
    Filter an animation to only include allowed elements.
    Used when animation only exists in seraph-faceless.
    Applies coordinate transforms to seraph elements.
    """
    filtered_anim = {
        k: v for k, v in anim.items() if k != 'keyframes'
    }
    
    filtered_keyframes = []
    for keyframe in anim.get('keyframes', []):
        filtered_elements = {}
        for k, v in keyframe['elements'].items():
            if k in SERAPH_ELEMENTS:
                # Apply seraph transforms when copying from seraph
                filtered_elements[k] = apply_seraph_transforms(v)
        
        if filtered_elements:  # Only add keyframe if it has elements
            filtered_keyframes.append({
                'frame': keyframe['frame'],
                'elements': filtered_elements
            })
    
    filtered_anim['keyframes'] = filtered_keyframes
    return filtered_anim


def merge_single_animation(seraph_anim, kemono_anim):
    """
    Merge a single animation that exists in both sources.
    For matching frame numbers, use specified elements from seraph and others from kemono.
    For non-matching frame numbers, add them as-is from their source.
    Applies coordinate transforms to seraph elements.
    """
    # Start with the kemono animation as base
    merged_anim = {
        k: v for k, v in kemono_anim.items() if k != 'keyframes'
    }
    
    # Create keyframe mappings
    seraph_keyframes = {kf['frame']: kf for kf in seraph_anim.get('keyframes', [])}
    kemono_keyframes = {kf['frame']: kf for kf in kemono_anim.get('keyframes', [])}
    
    all_frames = sorted(set(seraph_keyframes.keys()) | set(kemono_keyframes.keys()))
    
    merged_keyframes = []
    for frame in all_frames:
        seraph_kf = seraph_keyframes.get(frame)
        kemono_kf = kemono_keyframes.get(frame)
        
        if seraph_kf and kemono_kf:
            # Both have this frame - merge elements
            merged_elements = {}
            
            # Start with all elements from kemono
            merged_elements.update(kemono_kf['elements'])
            
            # Override with seraph elements for allowed bones (with transforms applied)
            for elem_name, elem_data in seraph_kf['elements'].items():
                if elem_name in SERAPH_ELEMENTS:
                    merged_elements[elem_name] = apply_seraph_transforms(elem_data)
            
            merged_keyframes.append({
                'frame': frame,
                'elements': merged_elements
            })
        elif seraph_kf:
            # Only in seraph - use filtered version with transforms
            filtered_elements = {}
            for k, v in seraph_kf['elements'].items():
                if k in SERAPH_ELEMENTS:
                    filtered_elements[k] = apply_seraph_transforms(v)
            if filtered_elements:
                merged_keyframes.append({
                    'frame': frame,
                    'elements': filtered_elements
                })
        else:
            # Only in kemono - use as-is
            merged_keyframes.append(kemono_kf)
    
    merged_anim['keyframes'] = merged_keyframes
    return merged_anim


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_mixed_animation_patch.py <seraph_source> <kemono_source> <output_patch>")
        sys.exit(1)
    
    seraph_file = sys.argv[1]
    kemono_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Merge animations
    merged_animations = merge_animations(seraph_file, kemono_file)
    
    # Create patch
    patch = {
        "file": "kemono:animations/kemono0_animations.json",
        "op": "replace",
        "path": "/animations",
        "value": merged_animations
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([patch], f, indent=4)
    
    print(f"Wrote merged animation patch to {output_file}")
    print(f"Total animations merged: {len(merged_animations)}")


if __name__ == "__main__":
    main()