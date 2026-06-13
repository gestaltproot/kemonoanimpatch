import json
import sys


def remap_rotation(rot_x, rot_y, rot_z):
    """
    90-ish degree Z-axis basis change.

    Option 1:
        X' = Y
        Y' = -X
        Z' = Z
    """
    return -rot_y, -rot_z, rot_x, 


def process_animation(data):
    animations = data[0].get("value", [])

    for animation in animations:
        for keyframe in animation.get("keyframes", []):
            elements = keyframe.get("elements", {})

            for bone_name, bone in elements.items():
                rx = bone.get("rotationX")
                ry = bone.get("rotationY")
                rz = bone.get("rotationZ")

                if rx is None and ry is None and rz is None:
                    continue

                rx = rx or 0.0
                ry = ry or 0.0
                rz = rz or 0.0

                new_rx, new_ry, new_rz = remap_rotation(rx, ry, rz)

                bone["rotationX"] = round(new_rx, 3)
                bone["rotationY"] = round(new_ry, 3)
                bone["rotationZ"] = round(new_rz, 3)

    return data


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py input.json output.json")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    data = process_animation(data)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Wrote converted animation to {sys.argv[2]}")


if __name__ == "__main__":
    main()