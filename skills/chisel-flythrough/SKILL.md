---
name: chisel-flythrough
description: Design a camera move with a 3D blockout, guide World Labs Atlas Chisel with camera-aligned depth, and render a continuous flythrough. Use for substantial parallax, occlusions, reverse angles, and scenes needing explicit spatial structure.
---

# Chisel flythrough

Start with the reveal and lay out the geometry the camera will pass. Give the foreground, subject and background distinct distances. Build the far side of anything the camera circles. A door needs a frame and an opening through its wall. For a person, block out head, torso, separated limbs, pose and the prop that identifies the action.

For a new blockout, author the layout in Chisel and save an editable `.chisel` project. Group the subject, foreground, background and cameras so each can be adjusted independently. Place guide cameras at the entrance, tightest clearance, turn and reveal. Open the saved project again and check those views before spending credits on a generation.

With the WLT source available, the same workflow can run headlessly. Use Chisel’s `createShapeSource` and `createGroupSource` for the editable layout, `cameraSourceFromPlacedPose` for guide cameras, and `writeSceneContainer` to save. Verify with `readSceneFile`, check for dropped nodes, and render the native geometry along the intended path. In the example/yolk-line directory, the project holds nine guide cameras and flight-path.json holds the full 144-frame move.

Animate one camera through the model. Scrub from start to end, checking clearances and silhouettes at the tightest turn. Sample the animation densely for the final flight and sparsely for guide views. Include guides where the camera sees a new surface or an object changes which landmark it occludes. In the singer example, 11 landscape guides support a 144-frame portrait shot from the same animated camera poses.

Export each guide's camera and forward-axis depth as a single-channel floating-point EXR. Express depth and translation in the same units. For a renderer that outputs distance along a unit ray, multiply by the ray's forward component to get axial depth. Write Atlas extrinsics in RUB (right/up/back), camera-to-world position and xyzw quaternion. Record actual width, height, fx, fy, cx and cy for each render. Export optional flat color hints with a PNG mask, white where colors condition the guide. A separate depth mask marks valid geometry. Keep shaded or log-scaled depth previews for inspection only.

Use Python 3, jq, FFmpeg, and an authenticated worldlabs CLI. Set PREP to this skill's scripts/prepare.py. Write scene.json with a prompt and a guides array. Each guide contains camera and depth (a relative EXR path), optionally depth_mask and the paired image and mask PNG paths. Add a reference_camera only if the style image depicts that pose. Write path.json as an ordered array of dense Atlas cameras. The repo's example/singer directory supplies both manifests and all guide inputs.

Prompt enhancement is enabled by default for guides and the final flight. Pass `--no-enhance-prompt` to a generation command in `prepare.py` to use the scene prompt verbatim for that pass.

~~~sh
worldlabs assets upload reference.jpg --json > reference.json
python3 "$PREP" guides scene.json --reference-id "$(jq -er '.id' reference.json)" > guide-request.json
worldlabs tasks run atlasChisel --request guide-request.json --wait --timeout 1800 --json > guides.json
worldlabs operations download "$(jq -er '.id' guides.json)" --out guides
~~~

Inspect each generated view beside its depth preview. Follow silhouettes and landmarks through occlusions. If a wall closes an opening, change the geometry. If a person merges with furniture, separate the silhouettes or add masked color hints. Rerender the affected guide set after a blockout change.

~~~sh
python3 "$PREP" flight scene.json --operation guides.json --path path.json > flight-request.json
worldlabs tasks run atlasGenerate --request flight-request.json --wait --timeout 1800 --json > flight.json
worldlabs operations download "$(jq -er '.id' flight.json)" --out frames
ffmpeg -framerate 24 -i frames/frames_%03d_image.jpg -c:v libx264 -pix_fmt yuv420p -movflags +faststart shot.mp4
~~~

Watch the turn at playback speed. For a side-by-side comparison, render the blockout from every final camera with matching intrinsics, timing and aspect ratio. For a trajectory overlay, project the actual camera centers onto a small ground grid and rotate the grid so opening travel points up-screen. Draw a moving camera frustum from the pose at the displayed frame.
