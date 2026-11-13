# Atlas and Chisel camera workflows

Two independent Codex skills for rendering camera moves with World Labs. Copy either directory from [skills](skills) into your Codex skills directory.

- [Atlas flythrough](skills/atlas-flythrough/SKILL.md) starts with a still image, builds support views, and renders a dense camera path.
- [Chisel flythrough](skills/chisel-flythrough/SKILL.md) starts with a 3D blockout, uses its depth to guide sparse views, then renders the camera move with Atlas.

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
