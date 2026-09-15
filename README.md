# Plasma Slalom

Full-colour Python 3 neon canyon-gate arcade for **ElbowOS**.

Steer a hover-boarder through a waving plasma canyon. Thread gold scoring gates, dodge magenta pillars, keep the combo alive.

Featured: [x.com/ElbowOS](https://x.com/ElbowOS)

Reel MP4 (9:16, 15s): [Google Drive](https://drive.google.com/file/d/1TjKJV5tusUAax0KjnenFuKG-NTnGrLZV/view?usp=drivesdk)

## Run

```bash
pip install -r requirements.txt
python3 plasma_slalom.py --play
```

- Left / Right or A / D — lean
- R — reset
- Esc — quit

## Record a 9:16 reel

```bash
python3 plasma_slalom.py --record
# or
ELBOWOS_RECORD=1 python3 plasma_slalom.py
```

Writes a 1080×1920 H.264 MP4 (15s @ 30fps) via ffmpeg. Default path: `/home/workdir/artifacts/PLASMA_SLALOM_ElbowOS.mp4`. Override with `ELBOWOS_MP4`.

Requires `pygame` and `ffmpeg`.
