# TikTok teaser

- `mangue-motion-1080x1080.mp4`: square teaser (1080×1080, 30 fps, about 32 s, stereo AAC soundtrack at about −14 LUFS)
- `mangue-cover-1080x1080.png`: cover image (hook question and stamp)

Structure: product image with a hook question and a stamp, the Maison DOUDJO Cabosse logo animation, the sector in numbers, the problem, local processing, and a "Le site arrive bientôt" end card with @BlackSun225.

## Soundtrack

"Du verger au port": original sound design and music synthesised in code (`source/sound.py`), with no samples and no copyrighted music. An original balafon theme (the wooden xylophone of the Senufo in the North, where the mangoes grow) follows the mango's journey.

- Dawn in the orchard: savanna birds, cicadas and wind; the balafon theme plays solo.
- "IMPORT UE SUSPENDU": the theme is cut off by a rubber-stamp hit and a metal slam.
- Logo: the full theme as a short sting, with a warm chord and a bell.
- The sector: djembe, dundun, shaker and bass groove; mangoes drop into a wooden crate as the counter climbs.
- The crisis: a ship's horn in the port, a container door slams, the theme in minor over a heartbeat, flies circling from left to right, a second stamp for the intercepted lots.
- Processing: the groove returns; each product has its sound (knife, pouring juice, blender, bubbling jam, ice, mortar and pestle).
- End card: the full theme, the orchard again, a chime on "Le site arrive bientôt", fade-out.

## Rebuild

`source/stage.html` draws every scene in SVG; `source/render.py` renders it frame by frame with Playwright (Chromium). The stage loads the Outfit and Geist Mono fonts and the Cabosse logo from local paths; adjust those paths before rendering on another machine.

```bash
python3 source/render.py source/stage.html A AR 0 4.2 30    # product + hook
python3 source/render.py source/stage.html B BR 0 22.9 30   # story + end card
ffmpeg -framerate 30 -i A/%04d.png -framerate 30 -i B/%04d.png -i cabosse-motion-1080x1080.mp4 -filter_complex \
 "[0:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[a];[2:v]fps=30,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[l];[1:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[b];[a][l]xfade=transition=fade:duration=0.3:offset=3.9[al];[al][b]xfade=transition=fade:duration=0.4:offset=9.0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 17 -r 30 -movflags +faststart silent.mp4
python3 source/sound.py 0.98    # writes mango_sound.wav (0.98 sets the loudness to about −14 LUFS)
ffmpeg -i silent.mp4 -i mango_sound.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart mangue-motion-1080x1080.mp4
```

The logo animation comes from [maison_doudjo_brand](https://github.com/BlackSun225/maison_doudjo_brand/tree/main/03-Motion).
