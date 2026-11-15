---
name: atlas-flythrough
description: Turn photographs or generated stills into depth-aware camera moves with World Labs Atlas. Use for walkthroughs, flyovers, reveals, or orbits through an image-based scene.
---

# Atlas flythrough

Choose what the viewer should discover by the end of the shot. Inspect the still for foreground edges, open travel space, and landmarks at several depths. An offset move past a foreground object makes scale easier to read. A reverse angle needs evidence of what lies behind the subject.

Use an authenticated World Labs CLI, Python 3 with NumPy, and FFmpeg. Work in a fresh shot directory. Set PREP to the absolute path of scripts/prepare.py in this skill. Supply a JPEG and its intended output dimensions.

Prompt enhancement is enabled by default for support views and the final flight. Pass `--no-enhance-prompt` to a generation command in `prepare.py` to use the scene prompt verbatim for that pass.

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

Inspect the supports in path order before the full render. Track the same landmark across neighboring angles. For an exact match to the input at frame zero, use the original posed camera there.

### Select anchors for a difficult move

For a passage, orbit or reverse reveal, scout both sides of the obstruction and the middle of the turn. Use the Developer API for Viewfinder-style stills. Run `atlasGenerate` with sparse `targetCameras`, `returnDepth: true` and `enhancePrompt: true`. A simple move with good coverage can use the first support pass.

Where the first pass is inconsistent, generate alternatives at **the same camera poses**. Keep the sparse target array and scene prompt fixed. Vary which reliable earlier posed views you supply in `contextFrames`, for example favor entrance-side views in one pass and exit-side views in another. Keep all cameras and depth maps in the same world coordinates.

Lay out the candidates with one column per camera time and one row per pass. Compare each candidate with the views on either side. Look for a continuous opening, a stable landmark silhouette, plausible foreground depth and a clear line of sight. Inspect depth on the surfaces the camera passes close to. Pick the views that agree across the sequence. Skip redundant or broken poses, or scout a missing angle before committing to the dense render.

To use a mixed selection, record each pick as a zero-based frame index in its saved operation. For example, after downloading and reviewing two six-view passes, build the final context with jq. Substitute your own picks. Keep the RGB asset, depth asset and camera together from the same returned frame.

~~~sh
# Save the picks so the same context can be rebuilt later.
echo '[["A",0],["B",2],["A",4],["B",5]]' > picks.json
jq -n --slurpfile a supports.json --slurpfile b alternate.json --slurpfile picks picks.json '
  {A: $a[0].response.frames, B: $b[0].response.frames} as $runs
  | [$picks[0][] as [$run, $i]
     | ($runs[$run][$i] // error("Unknown anchor: \($run)[\($i)]"))
     | {camera, imageAsset: {assetId: .imageAsset.assetId},
        depth: {depthAsset: {assetId: .depth.depthAsset.assetId}}}]
' > anchors.json
~~~

### Render and compare

Prepare the dense camera request from the shot keyframes.

~~~sh
python3 "$PREP" flight shot.json --pose pose.json --angles supports.json --frames 120 > flight-request.json
~~~

If you curated a mixed set, substitute those anchors now. This preserves the first posed image alongside the selected frames.

~~~sh
jq --slurpfile picks anchors.json '.contextFrames = [.contextFrames[0]] + $picks[0]' flight-request.json > selected-request.json
mv selected-request.json flight-request.json
~~~

Submit the complete path in one operation.

~~~sh
worldlabs tasks run atlasGenerate --request flight-request.json --wait --timeout 1800 --json > flight.json
worldlabs operations download "$(jq -er '.id' flight.json)" --out frames
ffmpeg -framerate 24 -i frames/frames_%03d_image.jpg -c:v libx264 -pix_fmt yuv420p -movflags +faststart shot.mp4
~~~

Inspect the start, widest baseline, reveal and end, then watch the clip at speed. If travel still reads like a zoom, keep the lens fixed and increase lateral travel near a supported foreground edge. Match endpoint position, heading, lens, and velocity when joining two moves meant to feel continuous. Optional --footfalls adds a subtle bob for walking shots.

When comparing anchor sets, render the same dense request twice, changing only `contextFrames`. If you revised the trajectory during scouting, rerun the old anchors on that revised trajectory. Use a distinct operation per request, save the requests, and check that deleting `contextFrames` leaves identical JSON. Show synchronized frames at the same timestamps, especially at the turn or reveal. Individual renders can still vary.

In the Tide Organ beach example, two API passes produced 40 stills at 20 poses. Seventeen picks covered the approach, ribbed arch, open surf and reverse view of shore. The copper pipe was a useful landmark for judging continuity during the offshore turn.
