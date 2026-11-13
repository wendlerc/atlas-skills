
# Film a day at ant height

Stage one action per shot. The bundled vertical JPEGs and matching JSON camera paths reproduce the setup for *The Crumb Run*. Dawn follows a floor seam toward a person making coffee. Noon edges past a knitted sock toward a crumb. Dusk follows the rug fringe toward ants carrying food home.

For a new story, generate or supply a 720 × 1280 portrait JPEG per shot. Put the lens against the floor. Give the ant a destination visible from the first frame, an object close enough to pass beside, and a human farther back for scale. Keep the passage beside the foreground object visible. This gives the camera somewhere to move and the viewer a way to judge depth.

## Run one shot

Use Python 3 with NumPy, FFmpeg, and the authenticated World Labs CLI (Node 22+). Set SKILL to the absolute path of this skill directory. Work in a separate output folder for each shot. Atlas tasks use project credits.

```sh
worldlabs auth status
shot=dawn
mkdir -p "$shot"
cd "$shot"
prep="$SKILL/scripts/prepare.py"
preset="$SKILL/assets/$shot.json"
python3 "$prep" pose "$SKILL/assets/$shot.jpg" > pose-request.json
worldlabs tasks run images2PosedRGBD --request pose-request.json --wait --json > pose.json
python3 "$prep" angles "$preset" --pose pose.json > angles-request.json
worldlabs tasks run atlasGenerate --request angles-request.json --wait --json > angles.json
worldlabs operations download "$(python3 -c 'import json; print(json.load(open("angles.json"))["id"])')" --out angles
```

Inspect the six downloaded RGB views in order. Follow the same floor seam, sock edge, or doorway across them. Look for near objects sliding against the background and for the destination staying recognizable. If the foreground stretches or the crumb disappears, shorten the sideways displacement and aim closer to the crumb. Generate fresh support views after changing the path. Resume a timed-out task with its operation ID.

## Render and assemble

```sh
python3 "$prep" flight "$preset" --pose pose.json --angles angles.json > flight-request.json
worldlabs tasks run atlasGenerate --request flight-request.json --wait --json > flight.json
worldlabs operations download "$(python3 -c 'import json; print(json.load(open("flight.json"))["id"])')" --out flight
ffmpeg -framerate 24 -i flight/frames_%03d_image.jpg -frames:v 120 -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart shot.mp4
```

The flight uses the original posed image and all six posed support images with depth. The helper samples the same path at 120 poses and adds a slight vertical and roll oscillation for footfalls. Watch all five seconds, especially as the camera passes the nearest object. Repeat from the output parent with shot=noon and shot=dusk. Join the three clips from that parent directory:

```sh
printf "file '%s/shot.mp4'\n" dawn noon dusk > cuts.txt
ffmpeg -f concat -safe 0 -i cuts.txt -c copy -movflags +faststart ant-day.mp4
```

## Adapt the camera

Copy a preset JSON into the output folder and point `preset` at the copy. Change its scene prompt and its keyframes together. Each row is `[time, x, y, z, aim_u, aim_v, aim_depth, focal_multiplier, roll_degrees]`. Time runs from 0 to 1. XYZ offsets are in the posed source camera's world units with right, up, and backward positive. Aim coordinates are fractions of the source image measured from the top left. Aim depth places the target along that image ray. A focal multiplier of 1 keeps the source lens. For a different scene, tune travel and aim depth to its estimated scale. Keep time strictly increasing with endpoints 0 and 1. Use nearby aim points for a tight turn around an object, and a farther point for a steady glide. Inspect the six views before launching the dense flight.
