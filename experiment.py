"""Rebuild the synthetic PDFs, actually compress them, and record measurements.
Run: python experiment.py   (Poppler pdftoppm must be on PATH)
No network access, personal documents, or external image assets are used.
"""
from pathlib import Path
from io import BytesIO
import csv, hashlib, json, math, platform, shutil, subprocess
import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFont
import pypdf, reportlab
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'
for folder in (DATA, ASSETS): folder.mkdir(exist_ok=True)
PAGE = (612, 792)  # US Letter, points
IMAGE_SIZE = (1800, 1200)
DISPLAY = (432, 288)  # Exactly 300 pixels/inch in each direction
TARGET = (720, 480)  # Exactly 120 pixels/inch at unchanged placement
KINDS = ('text', 'images', 'mixed')
PARAGRAPHS = [
    'A PDF is a container for text, images, fonts, and drawing instructions.',
    'Selectable text is stored as characters placed at coordinates on a page.',
    'A photograph is stored as a grid of pixels with a particular encoding.',
    'Reducing image resolution changes those pixels, not the page dimensions.',
    'A smaller download is useful only when the important details remain readable.',
    'Keep an original copy before changing a file that you plan to share.',
    'Check small labels, thin rules, punctuation, and numerical values after export.',
    'Text extraction is useful evidence but does not prove identical visual layout.',
    'A three-file demonstration cannot predict the result for every PDF.',
    'These pages contain synthetic material created only for this experiment.',
]

def art(page):
    # Original deterministic abstract raster, not a stock photo or scan.
    rng = np.random.default_rng(20261017 + page)
    yy, xx = np.mgrid[0:1200, 0:1800]
    a = np.empty((1200, 1800, 3), dtype=np.float64)
    a[:,:,0] = 115 + 63*np.sin(xx/123) + 24*np.cos(yy/73)
    a[:,:,1] = 145 + 57*np.sin((xx+yy)/172)
    a[:,:,2] = 163 + 55*np.cos((xx-yy)/218)
    a += rng.normal(0, 7, a.shape)
    im = Image.fromarray(np.clip(a,0,255).astype('uint8'))
    d = ImageDraw.Draw(im)
    d.rectangle((65,65,1735,325), fill='white')
    d.text((95,90), f'SYNTHETIC IMAGE / PAGE {page}', fill='#172e42', font=ImageFont.load_default(size=46))
    d.text((95,165), 'Fine labels: 0.125 | 8.36 | Q1 2026 | ABC xyz', fill='#172e42', font=ImageFont.load_default(size=30))
    d.text((95,225), 'Small raster text: 0123456789 / compare at the same scale', fill='#172e42', font=ImageFont.load_default(size=22))
    for i in range(32):
        x=95+i*14
        d.line((x,390,x,720), fill='white' if i%2 else '#142638', width=2)
    for i in range(7):
        x=700+i*130
        d.ellipse((x,440,x+92,532), fill=(20+i*26,90,155),outline='white',width=3)
    for i in range(12):
        d.line((700,610+i*10,1640,610+i*10), fill='#12253b',width=2)
    d.rectangle((65,950,1735,1125),fill='white')
    d.text((95,995),'Original procedural pixels; no personal or third-party images.',fill='#172e42',font=ImageFont.load_default(size=32))
    return im

def make_pdf(kind):
    path=DATA/f'{kind}-original.pdf'
    c=canvas.Canvas(str(path),pagesize=PAGE,pageCompression=1,invariant=1)
    c.setTitle(f'Synthetic compression test: {kind}')
    c.setAuthor('Idraaak')
    for p in range(1,4):
        if kind != 'images':
            c.setFont('Helvetica-Bold',20)
            c.drawString(54,744,f'Synthetic PDF: {kind} / {p}')
            c.setFont('Helvetica',10)
            c.drawString(54,721,'Three pages | Letter | Created for the PDF Compression Lab')
            t=c.beginText(54,685); t.setFont('Helvetica',10); t.setLeading(17)
            for line in PARAGRAPHS*(3 if kind=='text' else 1): t.textLine(line)
            c.drawText(t)
            c.setFont('Helvetica',7)
            c.drawString(54,55,f'Copy-check {kind} page {p}: ID-2048 | 0.125 | 8.36 | ABC xyz')
        if kind != 'text':
            c.drawImage(ImageReader(art(p)),90,186,width=DISPLAY[0],height=DISPLAY[1])
        c.showPage()
    c.save()
    return path

def compress(src):
    out=DATA/src.name.replace('-original','-compressed')
    w=PdfWriter(clone_from=src)
    dimensions=[]
    for page in w.pages:
        for img in list(page.images):
            before=img.image.size
            rgb=img.image.convert('RGB').resize(TARGET, Image.Resampling.LANCZOS)
            img.replace(rgb, quality=75, subsampling=2, optimize=False, progressive=False)
            dimensions.append({'before':before,'after':TARGET})
        page.compress_content_streams(level=9)
    w.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
    w.write(out)
    return out, dimensions

def render(path):
    exe=shutil.which('pdftoppm')
    if not exe: raise RuntimeError('Install Poppler and put pdftoppm on PATH')
    prefix=ASSETS/path.stem
    subprocess.run([exe,'-png','-r','144',str(path),str(prefix)],check=True,capture_output=True)
    return [ASSETS/f'{path.stem}-{i}.png' for i in range(1,4)]

def run():
    rows=[]; thumbs=[]
    for kind in KINDS:
        src=make_pdf(kind); out,dims=compress(src)
        a,b=PdfReader(src),PdfReader(out)
        ta=[p.extract_text() for p in a.pages]; tb=[p.extract_text() for p in b.pages]
        assert len(a.pages)==len(b.pages)==3
        assert ta==tb, 'Extracted text changed'
        # Confirm every output page keeps its text content, when present.
        assert all((bool(t)==(kind!='images')) for t in tb)
        rs,ro=render(src),render(out)
        for p in range(3):
            for mode,path in [('original',rs[p]),('compressed',ro[p])]:
                im=Image.open(path).convert('RGB'); im.thumbnail((306,396))
                cell=Image.new('RGB',(326,432),'#eef2f5'); cell.paste(im,(10,26))
                ImageDraw.Draw(cell).text((10,7),f'{kind} / {mode} / page {p+1}', fill='black')
                thumbs.append(cell)
        # Same coordinates and 144dpi; no rescaling between before/after.
        box=(180,636,1044,1212) if kind!='text' else (98,182,1090,540)
        for mode,path in [('original',rs[0]),('compressed',ro[0])]:
            Image.open(path).crop(box).save(ASSETS/f'{kind}-{mode}-crop.png')
        n,m=src.stat().st_size,out.stat().st_size
        rows.append({'kind':kind,'pages':3,'original_bytes':n,'compressed_bytes':m,
          'saving_percent':(n-m)/n*100,'text_identical':ta==tb,
          'original_text_characters':sum(map(len,ta)),
          'images':dims,'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
          'compressed_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
    sheet=Image.new('RGB',(326*6,432*3),'white')
    for i,im in enumerate(thumbs): sheet.paste(im,((i%6)*326,(i//6)*432))
    sheet.save(ASSETS/'all-pages-contact-sheet.png')
    result={'date':'2026-10-17','synthetic':True,'pages_per_document':3,
      'page_points':PAGE,'image_pixels_original':IMAGE_SIZE,'image_pixels_after':TARGET,
      'image_dpi_original':300,'image_dpi_after':120,'jpeg_quality':75,'jpeg_subsampling':2,
      'resample':'Pillow LANCZOS','content_stream_deflate_level':9,
      'object_cleanup':'compress_identical_objects(True, True)',
      'versions':{'python':platform.python_version(),'pypdf':pypdf.__version__,
      'Pillow':PIL.__version__,'reportlab':reportlab.Version,'numpy':np.__version__,
      'poppler':subprocess.run(['pdftoppm','-v'],capture_output=True,text=True).stderr.splitlines()[0]},
      'rows':rows}
    (DATA/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (DATA/'results.csv').open('w',newline='',encoding='utf-8') as f:
        cols=['kind','pages','original_bytes','compressed_bytes','saving_percent','text_identical','original_text_characters']
        cw=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore'); cw.writeheader(); cw.writerows(rows)
    print(json.dumps(result,indent=2))

if __name__=='__main__': run()
