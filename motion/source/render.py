import sys, os
from playwright.sync_api import sync_playwright
stage, outdir, mode, start, end, fps = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
times = [float(x) for x in sys.argv[7].split(',')] if len(sys.argv) > 7 else None
os.makedirs(outdir, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width':1080,'height':1080}, device_scale_factor=1)
    pg.goto('file://' + os.path.abspath(stage)); pg.wait_for_timeout(600)
    pg.evaluate('document.fonts.ready')
    if times is None:
        n = round((end - start) * fps)
        times = [start + i / fps for i in range(n)]
    for i, t in enumerate(times):
        pg.evaluate(f'render{mode}({t})')
        pg.screenshot(path=f'{outdir}/{i:04d}.png')
    b.close()
print(len(times), 'frames')
