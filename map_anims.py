import json
import sys

bone_rename_map = {
        "root": "b_Root",
        # "LowerTorso": "b_TorsoLower",
        # "UpperTorso": "b_TorsoUpper",
        # "UpperArmR": "b_ArmUpperR",
        # "UpperArmL": "b_ArmUpperL",
        # "LowerArmL": "b_ArmLowerL",
        # "LowerArmR": "b_ArmLowerR",
        # "ItemAnchor": "b_ItemAnchor",
        # "ItemAnchorL": "b_ItemAnchorL",
        "Neck": "b_Neck",
        "Head": "b_Head",
        "UpperFootR": "b_FootUpperR",
        "UpperFootL": "b_FootUpperL",
        "LowerFootR": "b_FootLowerR",
        "LowerFootL": "b_FootLowerL",
    }

def remap_rotation(rot_x, rot_y, rot_z):
    return -rot_y, rot_z, rot_x

def remap_position(pos_x, pos_y, pos_z):
    return -pos_y, -pos_z, pos_x

def process_keyframes(keyframes, ignore_anchor=True):
    for keyframe in keyframes:
            elements = keyframe.get("elements", {})

            for bone_name, bone in elements.items():
                
                valid_bones = set(bone_rename_map.values())
                if bone_name not in valid_bones:
                    continue
                
                rx = bone.get("rotationX")
                ry = bone.get("rotationY")
                rz = bone.get("rotationZ")

                px = bone.get("offsetX")
                py = bone.get("offsetY")
                pz = bone.get("offsetZ")

                if rx is None and ry is None and rz is None and px is None and py is None and pz is None:
                    continue

                rx = rx or 0.0
                ry = ry or 0.0
                rz = rz or 0.0

                new_rx, new_ry, new_rz = (0, 0, 0)
                new_rx, new_ry, new_rz = remap_rotation(rx, ry, rz)

                bone["rotationX"] = round(new_rx, 3)
                bone["rotationY"] = round(new_ry, 3)
                bone["rotationZ"] = round(new_rz, 3)
    
                if px is None and py is None and pz is None:
                    continue

                px = px or 0.0
                py = py or 0.0
                pz = pz or 0.0

                new_px, new_py, new_pz = remap_position(px, py, pz)

                bone["offsetX"] = round(new_px, 3)
                bone["offsetY"] = round(new_py, 3)
                bone["offsetZ"] = round(new_pz, 3)

def process_animation(data):
    animations = data.get("animations", [])

    for animation in animations:

        if animation.get("code") in ["wormgrunting", "wormgrunting-fp"]:  # Uses lots of leg changes, needs some offset adjustments
            keyframes = animation.get("keyframes", [])
            
            # keyframes = [
			# 	{
			# 		"frame": 0,
			# 		"elements": {
			# 			"UpperTorso": { "offsetX": 0.0, "offsetY": 0.0, "offsetZ": -0.5, "rotationX": -4.0, "rotationY": -14.0, "rotationZ": 8.0 },
			# 			"UpperArmR": { "offsetX": 1.0, "offsetY": -0.2, "offsetZ": 0.2, "rotationX": 0.0, "rotationY":-7.0 , "rotationZ": -78.0 },
			# 			"LowerArmR": { "offsetX": 0.0, "offsetY": 0.6, "offsetZ": 0.0, "rotationX": -32.0, "rotationY": 9.0, "rotationZ": -30.0 },
			# 			"ItemAnchor": { "offsetX": 1.2, "offsetY": 0.6, "offsetZ": -0.7, "rotationX": -16.0, "rotationY": 0.0, "rotationZ": 180.0 },
			# 			"UpperArmL": { "offsetX": 0.4, "offsetY": 0.0, "offsetZ": -0.4, "rotationX": -88.0, "rotationY": -46.0, "rotationZ": -81.0 },
			# 			"LowerArmL": { "offsetX": 0.1, "offsetY": 0.4, "offsetZ": 0.0, "rotationX": -15.0, "rotationY": -11.0, "rotationZ": -30.0 },
			# 			"b_Neck": { "rotationX": 0.0, "rotationY": 0.0, "rotationZ": 13.0 },
			# 			"b_Head": { "rotationX": 0.0, "rotationY": 0.0, "rotationZ": 13.0 },
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 16.0, "rotationZ": 15.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 3,
			# 		"elements": {
			# 			"UpperTorso": { "rotationX": -4.0, "rotationY": -15.0, "rotationZ": 14.0 },
			# 			"UpperArmR": { "offsetX": 1.0, "offsetY": -0.2, "offsetZ": 0.2, "rotationX": 0.0, "rotationY":-7.0 , "rotationZ": -78.0 },
			# 			"UpperArmL": { "offsetX": 0.4, "offsetY": -0.6, "offsetZ": -0.4, "rotationX": -88.0, "rotationY": -45.0, "rotationZ": -75.0 },
			# 			"LowerArmL": { "rotationX": -14.0, "rotationY": -9.0, "rotationZ": -37.0 },
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 19.0, "rotationZ": 16.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 4,
			# 		"elements": {
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 23.0, "rotationZ": 9.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 5,
			# 		"elements": {
			# 			"UpperTorso": { "offsetX": -0.2, "offsetY": 0.0, "offsetZ": -0.5 },
			# 			"UpperArmR": { "offsetX": 1.0, "offsetY": -0.2, "offsetZ": 0.2, "rotationX": 0.0, "rotationY":-7.0 , "rotationZ": -78.0 },
			# 			"UpperArmL": { "rotationX": -88.0, "rotationY": -46.1429, "rotationZ": -84.43 },
			# 			"LowerArmL": { "rotationX": -14.2857, "rotationY": -9.5714, "rotationZ": -21.5714 },
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 20.0, "rotationZ": 12.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 6,
			# 		"elements": {
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 21.0, "rotationZ": 6.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 7,
			# 		"elements": {
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 14.0, "rotationZ": 8.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 8,
			# 		"elements": {
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 16.0, "rotationZ": 3.5 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 9,
			# 		"elements": {
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 11.0, "rotationZ": 7.0 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 10,
			# 		"elements": {
			# 			"UpperArmL": { "offsetX": 0.1, "offsetY": -1.6, "offsetZ": -0.4, "rotationX": -61.0, "rotationY": -48.0, "rotationZ": -83.0 },
			# 			"LowerArmL": { "offsetX": 0.1, "offsetY": -0.2, "offsetZ": 0.0, "rotationX": -15.0, "rotationY": -11.0, "rotationZ": 3.0 },
			# 			"ItemAnchorL": { "rotationX": 0.0, "rotationY": 10.0, "rotationZ": 7.0 },
			# 			"UpperTorso": { "offsetX": -0.1, "offsetY": 0.0, "offsetZ": -0.5, "rotationX": -4.0, "rotationY": -16.0, "rotationZ": 18.0 },
			# 			"UpperArmR": { "offsetX": 1.0, "offsetY": -0.2, "offsetZ": 0.2, "rotationX": 0.0, "rotationY":-7.0 , "rotationZ": -78.0 },
			# 		}
			# 	},
			# 	{
			# 		"frame": 13,
			# 		"elements": {
			# 			"UpperArmL": { "offsetX": 0.4, "offsetY": -1.2, "offsetZ": -0.4 }
			# 		}
			# 	},
			# 	{
			# 		"frame": 17,
			# 		"elements": {
			# 			"UpperArmL": { "offsetX": 0.4, "offsetY": -0.2, "offsetZ": -0.4 }
			# 		}
			# 	}
			# ]
            # process_keyframes(keyframes, ignore_anchor=True)

            keyframes[0]["elements"].update(
                {
                    "LowerTorso": {
                            "rotShortestDistanceX": True,
                            "rotShortestDistanceY": True,
                            "rotShortestDistanceZ": True,
                            "rotationX": 0.0,
                            "rotationY": 0.0,
                            "rotationZ": 0.999995,
                            "offsetY": -6.31763124,
                            "offsetX": 2.69455051,
                            "offsetZ": -0.0
                        },
                        "b_FootUpperR": {
                            "rotShortestDistanceX": True,
                            "rotShortestDistanceY": True,
                            "rotShortestDistanceZ": True,
                            "rotationX": 5.44816656,
                            "rotationY": 25.30363456,
                            "rotationZ": -4.51232648,
                        },
                        "b_FootLowerR": {
                            "rotShortestDistanceX": True,
                            "rotShortestDistanceY": True,
                            "rotShortestDistanceZ": True,
                            "rotationX": -1.2199832,
                            "rotationY": -67.79344642,
                            "rotationZ": -1.2652315,
                            "offsetX": -0.33196646,
                            "offsetY": 0.0,
                            "offsetZ": -0.62433827
                        },
                    "b_FootUpperL": {
                            "rotShortestDistanceX": True,
                            "rotShortestDistanceY": True,
                            "rotShortestDistanceZ": True,
                            "rotationX": -5.44816442,
                            "rotationY": 0.30358959,
                            "rotationZ": 4.51232264,
                            "offsetX": -1.99365366,
                            "offsetY": -0.15893261,
                            "offsetZ": -0.00926066
                        },
                        "b_FootLowerL": {
                            "rotShortestDistanceX": True,
                            "rotShortestDistanceY": True,
                            "rotShortestDistanceZ": True,
                            "rotationX": 1.9e-07,
                            "rotationY": -67.49999334,
                            "rotationZ": 1.5e-07,
                            "offsetX": -1.23659217,
                            "offsetY": -0.0,
                            "offsetZ": -0.89489651
                        },
                    "b_Tail0": {

                            "rotationX": 0.34096651,
                            "rotationY": 0.73116124,
                            "rotationZ": -65.97233957
                        },
                        "b_Tail1": {

                            "rotationX": -0.56633415,
                            "rotationY": 0.57565896,
                            "rotationZ": -18.29400087
                        },
                        "b_Tail2": {

                            "rotationX": -0.67906851,
                            "rotationY": 0.42315853,
                            "rotationZ": -0.27453156
                        },
                        "b_Tail3": {

                            "rotationX": -0.81207278,
                            "rotationY": 0.17688791,
                            "rotationZ": 23.49058808
                        },
                        "b_Tail4": {

                            "rotationX": -0.54046209,
                            "rotationY": 0.59896533,
                            "rotationZ": 37.09428268
                        },
                        "b_Tail5": {

                            "rotationX": -0.20344978,
                            "rotationY": 0.7806791,
                            "rotationZ": 9.32616484
                        }
                }
            )
                
            animation["keyframes"] = keyframes

            continue

        process_keyframes(animation.get("keyframes", []))

    return data


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


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py input.json output.json")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    data = rename_bones(data)

    data = process_animation(data)

    # rewrite data into a patch format
    patch = {
        "file": "kemono:animations/kemono0_animations.json",
        "op": "addeach",
        "path": "/animations/-",
        "value": data.get("animations", [])
    }

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump([patch], f, indent=4)

    print(f"Wrote converted animation to {sys.argv[2]}")


if __name__ == "__main__":
    main()