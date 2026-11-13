"""Build Atlas Chisel guide and dense flythrough requests from portable files."""
import argparse
import base64
import json
from pathlib import Path


def image(path, mime):
    return {
        "base64": f"data:image/{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["guides", "flight"])
    parser.add_argument("scene", type=Path)
    parser.add_argument("--reference-id")
    parser.add_argument("--operation", type=Path)
    parser.add_argument("--path", type=Path)
    args = parser.parse_args()
    scene = json.loads(args.scene.read_text())
    common = dict(prompt=scene["prompt"], enhancePrompt=False)
    if args.stage == "guides":
        targets = []
        for guide in scene["guides"]:
            def asset(key, mime):
                return image(args.scene.parent / guide[key], mime)
            target = dict(camera=guide["camera"], depth={"depthAsset": asset("depth", "x-exr")})
            if "depth_mask" in guide:
                target["depth"]["maskAsset"] = asset("depth_mask", "png")
            if "image" in guide:
                target.update(imageAsset=asset("image", "png"), maskAsset=asset("mask", "png"))
            targets.append(target)
        body = dict(**common, targetFrames=targets, returnDepth=True, voxelSize=0)
        if args.reference_id:
            ref = {"assetId": args.reference_id}
            body["styleReferenceImageAsset"] = ref
            if "reference_camera" in scene:
                body["contextFrames"] = [dict(camera=scene["reference_camera"], imageAsset=ref)]
    else:
        if not args.operation or not args.path:
            parser.error("flight requires --operation and --path")
        op = json.loads(args.operation.read_text())
        if op.get("error") or not op.get("done"):
            parser.error("Expected a successful completed Chisel operation")
        frames = [dict(camera=f["camera"], imageAsset={"assetId": f["imageAsset"]["assetId"]},
                       depth={"depthAsset": {"assetId": f["depth"]["depthAsset"]["assetId"]}})
                  for f in op["response"]["frames"]]
        body = dict(**common, contextFrames=frames, targetCameras=json.loads(args.path.read_text()), returnDepth=False)
    print(json.dumps(body))


if __name__ == "__main__":
    main()
