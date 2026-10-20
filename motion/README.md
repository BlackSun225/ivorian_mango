# TikTok teaser

- `mangue-motion-1080x1080.mp4`: square teaser (1080×1080, 30 fps, about 32 s, no audio)
- `mangue-cover-1080x1080.png`: cover image (hook question and stamp)

Structure: product image with a hook question and a stamp, the Maison DOUDJO Cabosse logo animation, the sector in numbers, the problem, local processing, and a "Le site arrive bientôt" end card with @BlackSun225.

## Rebuild

`source/stage.html` draws every scene in SVG; `source/render.py` renders it frame by frame with Playwright (Chromium). The stage loads the Outfit and Geist Mono fonts and the Cabosse logo from local paths; adjust those paths before rendering on another machine.

```bash
python3 source/render.py source/stage.html A AR 0 4.2 30    # product + hook
python3 source/render.py source/stage.html B BR 0 22.9 30   # story + end card
ffmpeg -framerate 30 -i A/%04d.png -framerate 30 -i B/%04d.png -i cabosse-motion-1080x1080.mp4 -filter_complex \
 "[0:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[a];[2:v]fps=30,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[l];[1:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[b];[a][l]xfade=transition=fade:duration=0.3:offset=3.9[al];[al][b]xfade=transition=fade:duration=0.4:offset=9.0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 17 -r 30 -movflags +faststart mangue-motion-1080x1080.mp4
```

The logo animation comes from [maison_doudjo_brand](https://github.com/BlackSun225/maison_doudjo_brand/tree/main/03-Motion).
