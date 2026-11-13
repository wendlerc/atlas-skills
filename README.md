# The Crumb Run

A 15-second day in the life of an ant, filmed from floor level. [Watch the finished film](example/the-crumb-run.mp4).

Copy [atlas-ant-flythrough](atlas-ant-flythrough) into your Codex skills directory and ask: “Use $atlas-ant-flythrough to follow a breadcrumb across the kitchen.” The [skill instructions](atlas-ant-flythrough/SKILL.md) cover preparing a still, inspecting six Atlas support views, and rendering the full camera move.

| Shot | Source image | Editable path | All 120 camera poses | Support images and depth |
| --- | --- | --- | --- | --- |
| Dawn | [Kitchen](atlas-ant-flythrough/assets/dawn.jpg) | [Keyframes](atlas-ant-flythrough/assets/dawn.json) | [Trajectory](example/cameras/dawn-flight.json) | [Views](example/dawn-angles) |
| Noon | [Sock and crumb](atlas-ant-flythrough/assets/noon.jpg) | [Keyframes](atlas-ant-flythrough/assets/noon.json) | [Trajectory](example/cameras/noon-flight.json) | [Revised views](example/noon-crumbangles) |
| Dusk | [Return to the nest](atlas-ant-flythrough/assets/dusk.jpg) | [Keyframes](atlas-ant-flythrough/assets/dusk.json) | [Trajectory](example/cameras/dusk-flight.json) | [Views](example/dusk-angles) |

The [example directory](example) includes the original posed RGB and depth images, both noon support passes, and the rendered JPEGs in frame order. To rebuild the final edit locally, install NumPy, OpenCV for Python and FFmpeg, then run these commands from the repository root:

```sh
python3 example/edit/sound.py
python3 example/edit/edit.py
```

The edit adds animated antennae, synthesized sound and the closing fade. Run the Atlas workflow when you want to change the scene or camera path.
