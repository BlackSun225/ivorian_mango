# TikTok teaser

- `mangue-motion-1080x1080.mp4`: square teaser (1080×1080, 30 fps, about 32 s, stereo AAC soundtrack at about −14 LUFS)
- `mangue-cover-1080x1080.png`: cover image (hook question and stamp)

Structure: product image with a hook question and a stamp, the Maison DOUDJO Cabosse logo animation, the sector in numbers, the problem, local processing, and a "Le site arrive bientôt" end card with @BlackSun225.

## Soundtrack

An original piece synthesised in code (`source/sound.py`), with no samples and no copyrighted music. It is a West African-inspired groove at 100 BPM: balafon (the wooden xylophone of the Senufo in the North, where the mangoes grow), djembe, shaker and a soft bass, in C major pentatonic.

- Product and hook: light groove; a stamp impact when "IMPORT UE SUSPENDU" hits.
- Logo: the drums drop out, a warm pad and a bell chime.
- The sector: full groove; soft ticks while the counter climbs.
- The crisis: the background turns dark, the music moves to A minor with a heartbeat drum, and flies buzz around the mango.
- Processing: the groove comes back; each product pops with a balafon note.
- End card: a chime on "Le site arrive bientôt", then a fade-out.

## Rebuild

`source/stage.html` draws every scene in SVG; `source/render.py` renders it frame by frame with Playwright (Chromium). The stage loads the Outfit and Geist Mono fonts and the Cabosse logo from local paths; adjust those paths before rendering on another machine.

```bash
python3 source/render.py source/stage.html A AR 0 4.2 30    # product + hook
python3 source/render.py source/stage.html B BR 0 22.9 30   # story + end card
ffmpeg -framerate 30 -i A/%04d.png -framerate 30 -i B/%04d.png -i cabosse-motion-1080x1080.mp4 -filter_complex \
 "[0:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[a];[2:v]fps=30,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[l];[1:v]format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[b];[a][l]xfade=transition=fade:duration=0.3:offset=3.9[al];[al][b]xfade=transition=fade:duration=0.4:offset=9.0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 17 -r 30 -movflags +faststart silent.mp4
python3 source/sound.py 0.87    # writes mango_sound.wav (0.87 sets the loudness to about −14 LUFS)
ffmpeg -i silent.mp4 -i mango_sound.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart mangue-motion-1080x1080.mp4
```

The logo animation comes from [maison_doudjo_brand](https://github.com/BlackSun225/maison_doudjo_brand/tree/main/03-Motion).
