---
name: atlas-flythrough
description: Turn photographs or generated stills into depth-aware camera moves with World Labs Atlas. Use for walkthroughs, flyovers, reveals, or orbits through an image-based scene.
---

# Atlas flythrough

Choose what the viewer should discover by the end of the shot. Inspect the still for foreground edges, open travel space, and landmarks at several depths. An offset move past a foreground object makes scale easier to read. A reverse angle needs evidence of what lies behind the subject.

Use an authenticated World Labs CLI, Python 3 with NumPy, and FFmpeg. Work in a fresh shot directory. Set PREP to the absolute path of scripts/prepare.py in this skill. Supply a JPEG and its intended output dimensions.

~~~sh
python3 "$PREP" pose scene.jpg --resolution 1280 720 > pose-request.json
worldlabs tasks run images2PosedRGBD --request pose-request.json --wait --json > pose.json
~~~

Write shot.json with a scene prompt and keyframes. Each row specifies normalized time, camera-local XYZ travel (right, up, backward), normalized image-space aim U and V (from top left), aim depth in source-camera units, focal multiplier and bank in degrees. Keep time strictly increasing from 0 to 1. Inspect the estimated depth to choose distances in the scene's scale. This minimal lateral move is a starting point:

~~~json
{"prompt":"A sunlit workshop with a workbench and tall windows.","knots":[[0,0,0,0,0.5,0.5,2,1,0],[0.5,0.15,0,-0.12,0.53,0.5,2,1,0],[1,0.35,0,-0.25,0.57,0.5,2,1,0]]}
~~~

~~~sh
python3 "$PREP" angles shot.json --pose pose.json --supports 6 > supports-request.json
worldlabs tasks run atlasGenerate --request supports-request.json --wait --json > supports.json
worldlabs operations download "$(jq -er '.id' supports.json)" --out supports
~~~

Inspect all supports in order. Track the same landmark across angles. If it slides, grows a duplicate, or disappears, shorten the unsupported part of the move or establish the missing view first. For larger reveals, generate intermediate views in rounds, passing reliable earlier RGB, camera and depth triplets in contextFrames. Keep every pose in the same coordinate system. For an exact match to the input at frame zero, use the original posed camera there.

~~~sh
python3 "$PREP" flight shot.json --pose pose.json --angles supports.json --frames 120 > flight-request.json
worldlabs tasks run atlasGenerate --request flight-request.json --wait --timeout 1800 --json > flight.json
worldlabs operations download "$(jq -er '.id' flight.json)" --out frames
ffmpeg -framerate 24 -i frames/frames_%03d_image.jpg -c:v libx264 -pix_fmt yuv420p -movflags +faststart shot.mp4
~~~

Inspect the start, widest baseline, reveal and end, then watch the clip at speed. If travel still reads like a zoom, keep the lens fixed and increase lateral travel near a supported foreground edge. Match endpoint position, heading, lens, and velocity when joining two moves meant to feel continuous. Optional --footfalls adds a subtle bob for walking shots.
