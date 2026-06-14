# Kemono Animation Patches
Restores missing animations on the 0.1.17 version of Kemono for the fishing rod, snow shovel, and worm grunter. Also adds Combat Overhaul compatibility to the kemono model.

## How it was made
- allanims.json: previous experiments with combat overhaul compatibility
- kemono-body.json: previous experiments with combat overhaul compatibility
- horse.json: generated from the map_anims.py script (at d22b998) from vanilla animation data
- kemono.json: generated with the map_anims.py script from vanilla animation data

Unfortunately my notes and scripts on those previous experiments with combat overhaul compatibility were lost, the code for it in my repo isn't 100% accurate.
The good news is the data I did generate during those experiments works very well, so I am adding it here.

An unfortunate side-effect of doing the bone name remappings (which is required for combat overhaul to work) is that leg animations become very unpredictable.

This was written with the help of generative AI to assist with Harmony patching and writing out tedious parts of the scripts.