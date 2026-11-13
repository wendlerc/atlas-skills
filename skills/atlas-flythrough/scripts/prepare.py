"""Prepare Atlas requests from a JPEG, a shot preset, and saved operations."""
import argparse
import base64
import json
import math
from pathlib import Path

import numpy as np


def mul(a, b):
    return np.r_[a[3] * b[:3] + b[3] * a[:3] + np.cross(a[:3], b[:3]), a[3] * b[3] - a[:3] @ b[:3]]

def quat(mat):
    k = np.empty((4, 4))
    k[:3, :3] = mat + mat.T - np.eye(3) * np.trace(mat)
    k[:3, 3] = k[3, :3] = [mat[2, 1] - mat[1, 2], mat[0, 2] - mat[2, 0], mat[1, 0] - mat[0, 1]]
    k[3, 3] = np.trace(mat)
    (_, vs) = np.linalg.eigh(k)
    q = vs[:, -1]
    return q if q[3] >= 0 else -q

def unit(x):
    return x / np.linalg.norm(x)

def cam_at(src, p):
    (x, y, z, u, v, depth, lens, bank) = p
    o = src['extrinsics']
    k = src['intrinsics']
    q = np.array(o['quaternion'])
    conj = q.copy()
    conj[:3] *= -1
    eye = np.array([x, y, z])
    goal = np.array([(u * k['width'] - k['cx']) / k['fx'] * depth, (k['cy'] - v * k['height']) / k['fy'] * depth, -depth])
    back = unit(eye - goal)
    right = unit(np.cross([0, 1, 0], back))
    up = unit(np.cross(back, right))
    a = math.radians(bank)
    ori = quat(np.column_stack([right * np.cos(a) + up * np.sin(a), up * np.cos(a) - right * np.sin(a), back]))
    pos = o['position'] + mul(mul(q, np.r_[eye, 0]), conj)[:3]
    k = k.copy()
    k['fx'] *= lens
    k['fy'] *= lens
    return {'extrinsics': {'position': pos.tolist(), 'quaternion': mul(q, ori).tolist(), 'coordinateSystem': 'rub'}, 'intrinsics': k}

def interp(knots, ts):
    knots = np.array(knots)
    x = knots[:, 0]
    y = knots[:, 1:]
    s = np.zeros_like(y)
    for i in range(1, len(x) - 1):
        a = (y[i] - y[i - 1]) / (x[i] - x[i - 1])
        b = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
        m = a * b > 0
        s[i, m] = 2 / (1 / a[m] + 1 / b[m])
    for t in ts:
        i = min(len(x) - 2, np.searchsorted(x[1:], t))
        h = x[i + 1] - x[i]
        f = (t - x[i]) / h
        yield ((1 - 3 * f * f + 2 * f ** 3) * y[i] + h * f * (1 - f) ** 2 * s[i] + (3 * f * f - 2 * f ** 3) * y[i + 1] + h * f * f * (f - 1) * s[i + 1])


def context(path):
    operation = json.loads(path.read_text())
    if operation.get('error') or not operation.get('done'):
        raise ValueError(f'Expected a successful finished operation in {path}')
    return [
        dict(camera=frame['camera'],
             imageAsset={'assetId': frame['imageAsset']['assetId']},
             depth={'depthAsset': {'assetId': frame['depth']['depthAsset']['assetId']}})
        for frame in operation['response']['frames']
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('pose', 'angles', 'flight'))
    parser.add_argument('input', type=Path, help='JPEG for pose, shot JSON otherwise')
    parser.add_argument('--pose', type=Path)
    parser.add_argument('--angles', type=Path)
    parser.add_argument('--resolution', type=int, nargs=2, default=[720, 1280], metavar=('WIDTH','HEIGHT'))
    parser.add_argument('--frames', type=int, default=120)
    parser.add_argument('--supports', type=int, default=6)
    parser.add_argument('--footfalls', action='store_true', help='Add a tiny walking bob')
    args = parser.parse_args()
    if min(args.frames, args.supports, *args.resolution) < 1:
        parser.error('Counts and dimensions must be positive')
    if args.stage == 'pose':
        data = base64.b64encode(args.input.read_bytes()).decode('ascii')
        request = dict(frames=[dict(imageAsset={'base64': 'data:image/jpeg;base64,' + data})],
                       targetResolution=args.resolution)
    else:
        if not args.pose or (args.stage == 'flight' and not args.angles):
            parser.error('Angles and flight require --pose. Flight also requires --angles.')
        shot = json.loads(args.input.read_text())
        frames = context(args.pose)
        support = args.stage == 'angles'
        times = np.linspace(0, 1, args.supports if support else args.frames)
        cameras = []
        for t, controls in zip(times, interp(shot['knots'], times)):
            if not support and args.footfalls:
                envelope = np.sin(np.pi * t)
                controls[1] += .0008 * np.sin(t * 66) * envelope
                controls[7] += .22 * np.sin(t * 51) * envelope
            cameras.append(cam_at(frames[0]['camera'], controls))
        if not support:
            frames.extend(context(args.angles))
        request = dict(contextFrames=frames, targetCameras=cameras, returnDepth=support,
                       enhancePrompt=False, prompt=shot['prompt'])
    print(json.dumps(request))


if __name__ == '__main__':
    main()
