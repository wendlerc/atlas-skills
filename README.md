# Atlas and Chisel camera workflows

Two independent Codex skills for rendering camera moves with World Labs.

- [Atlas flythrough](skills/atlas-flythrough/SKILL.md) starts with a still image, builds support views, and renders a dense camera path.
- [Chisel flythrough](skills/chisel-flythrough/SKILL.md) starts with a 3D blockout, uses its depth to guide sparse views, then renders the camera move with Atlas.

## Quickstart

Paste this into Codex from an account with GitHub access to this repository:

> Use $skill-installer to install both skills from `wendlerc/atlas-skills`: `skills/atlas-flythrough` and `skills/chisel-flythrough`.

For rendering, install the World Labs CLI with `npm install -g @worldlabsai/cli` (Node.js 22+) and sign in with `worldlabs auth login`. The workflows also use Python 3, NumPy, FFmpeg and jq. On your next Codex turn, try either prompt.

**Atlas · start with a photo**  
Attach a photo of a room with a table in the foreground, then ask:

> Use $atlas-flythrough on this photo. Make a five-second shot that starts in the doorway, glides past the left edge of the table, and turns toward the window. Inspect the support views for parallax before rendering the MP4.

**Chisel · start with a blockout**

> Use $chisel-flythrough to build a lighthouse stairwell. Fly up the spiral stairs, pass behind the central column, and reveal the sea through the lantern-room windows. Render six seconds and show the blockout beside the finished shot.

**Prompt enhancement.** Both helpers explicitly send `enhancePrompt: false` for guide or support generation and the final flight. This carries the authored scene description through both passes. To try enhancement on a new scene, set `enhancePrompt` to `true` in the first generation request, then reuse the returned `promptUsed` with enhancement off for the flight.

## Example films

[The Crumb Run](example/the-crumb-run.mp4) is a 15-second ant-eye film. The [original recipe](example/ant-recipe/README.md) includes its walking motion. The [singer example](example/singer) shows the Chisel inputs and one generated view.

| Shot | Source image | Editable path | All 120 camera poses | Support images and depth |
| --- | --- | --- | --- | --- |
| Dawn | [Kitchen](example/ant-recipe/assets/dawn.jpg) | [Keyframes](example/ant-recipe/assets/dawn.json) | [Trajectory](example/cameras/dawn-flight.json) | [Views](example/dawn-angles) |
| Noon | [Sock and crumb](example/ant-recipe/assets/noon.jpg) | [Keyframes](example/ant-recipe/assets/noon.json) | [Trajectory](example/cameras/noon-flight.json) | [Revised views](example/noon-crumbangles) |
| Dusk | [Return to the nest](example/ant-recipe/assets/dusk.jpg) | [Keyframes](example/ant-recipe/assets/dusk.json) | [Trajectory](example/cameras/dusk-flight.json) | [Views](example/dusk-angles) |

The [example directory](example) includes the original posed RGB and depth images, both noon support passes, and the rendered JPEGs in frame order. To rebuild the final edit locally, install NumPy, OpenCV for Python and FFmpeg, then run these commands from the repository root:

```sh
python3 example/edit/sound.py
python3 example/edit/edit.py
```

The edit adds animated antennae, synthesized sound and the closing fade. Run the Atlas workflow when you want to change the scene or camera path.

The linked MP4 is a smaller playback copy. To recover the original 720 × 1280 master byte for byte, run:

~~~sh
cat example/master/the-crumb-run.part-* > the-crumb-run-master.mp4
~~~

Master SHA-256: `62bb29765edbdb02ec629bbe894f35092b7a156d4eff5d7d9bd0055747278867`.
