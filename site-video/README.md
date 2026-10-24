# TikTok website video

- `mangue-site-tiktok-590x1280.mp4`: phone screen recording of the live site, https://ivorianmango.maisondoudjo.com (590×1280, 60 fps, about 3 min 21 s, stereo AAC, about −13 LUFS)
- `mangue-site-music.mp3`: the soundtrack on its own

The video opens and closes on the Maison DOUDJO Cabosse logo (color version, on Pulp White `#FBF4EA`): 1.5 s at the start, fading into the recording, and about 2 s at the end. The last second of the recording, where the phone's screen-recording panel appears, was cut. The original sound of the recording was replaced by the music.

## Soundtrack

An original track synthesised in code (`source/compose.py`), with no samples and no copyrighted music. It is a warm West African groove at 100 BPM in A minor / C major (Am, F, C, G): a balafon-style melody with rolls on long notes, bass, shaker, hand claps and djembe-style hits.

- 0:00 soft intro on the logo (pad and balafon)
- 0:10 shaker and bass join
- 0:29 full groove and the main theme
- 1:07 busier balafon ostinato
- 1:26 theme again, with djembe
- 2:05 calmer section
- 2:24 full groove, theme doubled an octave higher
- 3:02 winding down, final A minor chord fading out on the closing logo

## Rebuild

`source/logo-card-590x1280.png` is the logo card: `02-Cabosse-secondary/svg/cabosse-stacked-color.svg` from [maison_doudjo_brand](https://github.com/BlackSun225/maison_doudjo_brand), 400 px wide, centered on a 590×1280 Pulp White frame.

```bash
python3 source/compose.py    # needs numpy and scipy; writes music.wav (200.7 s)

# logo intro + recording + logo outro, with the recording trimmed to 197.1 s
ffmpeg -loop 1 -framerate 60 -t 1.8 -i source/logo-card-590x1280.png -i recording.mp4 \
 -loop 1 -framerate 60 -t 2.5 -i source/logo-card-590x1280.png -filter_complex \
 "[0:v]format=yuv420p,setsar=1,settb=1/60[a];[1:v]trim=0:197.1,setpts=PTS-STARTPTS,fps=60,format=yuv420p,setsar=1,settb=1/60[v];[2:v]format=yuv420p,setsar=1,settb=1/60[b];[a][v]xfade=transition=fade:duration=0.3:offset=1.5[av];[av][b]xfade=transition=fade:duration=0.4:offset=198.2[outv]" \
 -map "[outv]" -c:v libx264 -crf 18 -pix_fmt yuv420p -r 60 -t 200.7 silent.mp4

ffmpeg -i silent.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ac 2 -t 200.7 -movflags +faststart mangue-site-tiktok-590x1280.mp4
```
