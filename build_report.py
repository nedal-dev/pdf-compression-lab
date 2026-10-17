"""Build the static report from recorded experiment results (never substitute data)."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/'data/results.json').read_text())
names={'text':'Selectable text','images':'High-resolution images','mixed':'Text + images'}
rows=''
for r in d['rows']:
    k=r['kind']
    rows+=f'''<tr><th scope="row">{names[k]}</th><td>3</td><td>{r['original_bytes']:,}</td><td>{r['compressed_bytes']:,}</td><td>{r['saving_percent']:.2f}%</td><td>{'No text layer in either file' if k=='images' else 'Identical extracted text on all 3 pages'}</td></tr>'''

def chart():
    # Separate, explicitly labeled linear scales keep the tiny text file readable.
    out=['<svg viewBox="0 0 860 410" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">PDF size before and after compression</title><desc id="chart-desc">Text uses a kilobyte scale; the two image documents use a separate megabyte scale. All scales start at zero. Exact byte values are in the table.</desc>']
    out.append('<rect x="22" y="12" width="15" height="15" fill="#173e62"/><text x="44" y="25">Original</text><rect x="150" y="12" width="15" height="15" fill="#c75c2e"/><text x="172" y="25">Compressed</text>')
    for j,rs in enumerate([d['rows'][:1],d['rows'][1:]]):
        top=65 if j==0 else 213; maximum=5 if j==0 else 15; div=1000 if j==0 else 1000000
        unit='kB (1,000 bytes)' if j==0 else 'MB (1,000,000 bytes)'
        out.append(f'<text x="22" y="{top}" class="chart-sub">{unit} · separate linear scale</text>')
        for tick in range(6):
            x=220+tick*112
            out.append(f'<line x1="{x}" y1="{top+12}" x2="{x}" y2="{top+50+len(rs)*43}" stroke="#d8e1e8"/><text x="{x}" y="{top+32+len(rs)*43+40}" text-anchor="middle">{maximum*tick/5:g}</text>')
        for i,r in enumerate(rs):
            y=top+30+i*59
            out.append(f'<text x="22" y="{y+15}">{names[r["kind"]]}</text>')
            for offset,key,col in [(0,'original_bytes','#173e62'),(19,'compressed_bytes','#c75c2e')]:
                val=r[key]/div; width=val/maximum*560
                out.append(f'<rect x="220" y="{y+offset}" width="{width:.3f}" height="14" fill="{col}"/><text x="{min(790,227+width):.3f}" y="{y+offset+12}" font-size="12">{val:.3f}</text>')
    out.append('</svg>');return ''.join(out)

crops=''
for k in ('images','mixed','text'):
    crops+=f'<h3>{names[k]}</h3><div class="pair">'
    for mode in ('original','compressed'):
        crops+=f'<figure><figcaption>{mode.title()} · page 1 · 144 dpi render</figcaption><a href="assets/{k}-{mode}-crop.png"><img src="assets/{k}-{mode}-crop.png" alt="Actual {mode} page-one crop of the {names[k].lower()} PDF" width="{992 if k=="text" else 864}" height="{358 if k=="text" else 576}" loading="lazy"></a></figure>'
    crops+='</div>'
canonical=(ROOT/'canonical.txt').read_text().strip() if (ROOT/'canonical.txt').exists() else ''
canonical_tag=f'<link rel="canonical" href="{canonical}">' if canonical else ''
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Why Some PDFs Shrink Dramatically—and Others Barely Change</title>
<meta name="description" content="A reproducible three-file PDF experiment: real byte counts, preserved selectable text, and actual before-and-after crops reveal what image compression trades away.">
CANONICAL
<meta name="robots" content="index,follow"><meta name="color-scheme" content="light">
<style>
:root{--ink:#172e42;--muted:#4c6272;--navy:#173e62;--orange:#c75c2e;--line:#d8e1e8;--paper:#fff;--tint:#f2f6f8}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.7 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1080px;margin:auto;padding:44px 28px 64px}header{max-width:900px;border-top:6px solid var(--navy);padding-top:22px}.eyebrow{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700}h1{font-size:clamp(32px,4.7vw,54px);line-height:1.12;letter-spacing:-.035em;margin:18px 0 24px}h2{font-size:28px;line-height:1.25;margin:0 0 18px}h3{font-size:20px;margin:26px 0 12px}p{max-width:820px;margin:0 0 18px}section{margin-top:44px;padding-top:30px;border-top:1px solid var(--line)}a{color:#075997;text-underline-offset:3px;overflow-wrap:anywhere}a:hover{color:#a7441c}.dek{font-size:21px;line-height:1.55}.byline,.note,figcaption{font-size:14px;color:var(--muted)}.finding{background:var(--tint);border-left:4px solid var(--orange);padding:20px 24px;margin:26px 0}.finding p:last-child{margin:0}.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:5px}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.5}th,td{text-align:left;vertical-align:top;padding:14px;border-bottom:1px solid var(--line)}thead{background:var(--tint)}tbody th{min-width:155px}td:nth-child(3),td:nth-child(4),td:nth-child(5){white-space:nowrap;font-variant-numeric:tabular-nums}caption{text-align:left;padding:14px;font-weight:600}svg{width:100%;height:auto;display:block;margin-top:18px}svg text{fill:var(--ink);font-family:system-ui,sans-serif;font-size:14px}.chart-sub{font-weight:700}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;min-width:0}figure img{display:block;width:100%;height:auto;border:1px solid var(--line);margin-top:8px}code,pre{font:13px/1.6 ui-monospace,Consolas,monospace}code{background:var(--tint);padding:2px 4px}pre{overflow-x:auto;background:var(--tint);padding:20px;border:1px solid var(--line)}li{max-width:810px;margin:9px 0}details{padding:16px 20px;background:var(--tint);margin:20px 0}summary{cursor:pointer;font-weight:600}.downloads{display:flex;gap:14px;flex-wrap:wrap}.downloads a{font-size:14px}footer{margin-top:48px;padding-top:24px;border-top:2px solid var(--navy);font-size:14px;color:var(--muted)}@media(max-width:620px){main{padding:22px 18px 40px}.pair{grid-template-columns:1fr}.dek{font-size:19px}h2{font-size:25px}section{margin-top:32px;padding-top:24px}.finding{padding:16px}.byline{line-height:1.6}}@media print{details{display:block}main{max-width:none}a{color:inherit}}
</style></head><body><main>
<header><div class="eyebrow">Idraaak · PDF Compression Lab</div>
<h1>Why Some PDFs Shrink Dramatically—and Others Barely Change</h1>
<p class="dek">Three PDFs. Three pages each. One compression pipeline. The image files became much smaller, but the tiny text file had only a few hundred bytes to give up.</p>
<p class="byline">Published by Nedal / Idraaak · Experiment: 17 October 2026 · Original synthetic documents · AI-assisted code, analysis, and writing</p>
</header>
<div class="finding"><p><strong>The measured result:</strong> selectable text fell from 4,532 to 3,896 bytes (14.03%, just 636 bytes). Images fell from 14.210 MB to 0.117 MB (99.18%); text plus images fell from 14.212 MB to 0.119 MB (99.16%).</p><p>Those large savings came with softer raster labels and lost fine texture. These deliberately lossless, high-resolution synthetic images had unusually large room for reduction. This is an illustration of the mechanism, not an expected saving for your files.</p></div>
<section id="question"><h2>What is actually taking up the space?</h2>
<p>A PDF can store selectable characters, drawing instructions, fonts, and embedded pixel images. Two documents with the same page count can therefore start at very different sizes. A compressor that mostly changes images has little to work on in a compact text document.</p>
<p>This experiment asks what happens when the same image-focused settings are applied to three known inputs. It does not compare compression services or attempt to find the best PDF tool.</p></section>
<section id="method"><h2>Three controlled inputs, one local pipeline</h2>
<p>Each original is a three-page US Letter PDF (612 × 792 points), generated with ReportLab 4.4.9 with page-stream compression already enabled. All content was created for this experiment; no personal documents, stock photographs, or copyrighted third-party images were used.</p>
<ul><li><strong>Selectable text:</strong> Helvetica headings, original explanatory sentences, repeated body text, and a 7-point copy-check footer. No embedded raster images.</li><li><strong>High-resolution images:</strong> one original procedural raster per page, containing gradients, seeded noise, fine rules, colored circles, and small raster labels. Each image is 1,800 × 1,200 pixels, stored losslessly and placed at 432 × 288 points: 300 dpi. It has no selectable text layer.</li><li><strong>Text + images:</strong> selectable headings, body text and footer plus exactly the same three images at the same physical size and position.</li></ul>
<p>The local tool is the included Python pipeline: <strong>pypdf 6.10.0 + Pillow 12.3.0</strong>, run with Python 3.12.14 and NumPy 2.3.5. For every image it resizes to 720 × 480 pixels (120 dpi) with LANCZOS, then writes JPEG at quality 75, chroma subsampling 2 (4:2:0), without progressive or optimized encoding. It compresses page streams with deflate level 9 and merges identical objects/removes unreferenced ones. Page count, page size, image placement, and text operators are retained. The text-only file goes through the same pipeline but has no images to resize.</p>
<p>This is <strong>lossy image compression</strong>, not a promise of unchanged image quality. There is one fixed setting, no repeated tuning, and no claim that 120 dpi suits every use.</p>
<details><summary>Exact procedure and reusable files</summary><p>Install the pinned Python dependencies in <a href="requirements.txt">requirements.txt</a> and install Poppler separately. Run <code>python experiment.py</code>, followed by <code>python build_report.py</code>. The script generates originals, compresses them, measures on-disk bytes, checks every page’s extracted text, renders every page with Poppler 26.07.0 at 144 dpi, and crops page 1 at identical coordinates.</p><pre>python -m pip install -r requirements.txt
python experiment.py
python build_report.py</pre><p>Seed: 20261017 + page number, with NumPy default_rng. Exact software versions and SHA-256 hashes for all six PDFs are in <a href="data/results.json">results.json</a>. Different library or renderer versions can change bytes and pixels. The stored files are the evidence for this run.</p></details></section>
<section id="results"><h2>The actual file sizes</h2><p>Saving = (original bytes − compressed bytes) ÷ original bytes × 100. Values below come from the six files on disk; percentages are rounded to two decimals. kB and MB in this report are decimal units.</p>
<div class="table-wrap"><table><caption>Measured results · three pages per file</caption><thead><tr><th scope="col">Content</th><th scope="col">Pages</th><th scope="col">Original bytes</th><th scope="col">After bytes</th><th scope="col">Saving</th><th scope="col">Text check</th></tr></thead><tbody>ROWS</tbody></table></div>
CHART
<p class="note">The upper panel uses kB; the lower panel uses MB. Each scale is linear and starts at zero. The separate scales make the tiny text file visible without implying that it was comparable in size to the image files.</p>
<div class="downloads"><a href="data/results.csv">Download CSV</a><a href="data/results.json">Full measurements and hashes</a><a href="https://github.com/nedal-dev/pdf-compression-lab">Source and reproduction scripts</a></div></section>
<section id="visual"><h2>Smaller files, softer image detail</h2><p>These are real crops from the original and compressed PDFs, rendered at the same 144 dpi with the same coordinates. Each pair has equal pixel dimensions and equal display width. Open a crop to inspect its actual pixels; a narrow screen can hide differences.</p>
CROPS
<p><strong>Visual observations:</strong> all 18 rendered pages retained their expected layout and content. The image crops show smoother backgrounds, softened small raster lettering, and less distinct thin lines after compression. The larger labels and colored shapes remain recognizable. In the text-only pages and the selectable text of the mixed file, no visible layout or character changes were observed at the inspected render scale.</p>
<p>Every text-containing page returned identical extracted text before and after: 7,044 characters across the text PDF and 2,634 across the mixed PDF. Their text layer remains available for selection and copying; the script does not rasterize it. The image-only PDF has zero extracted characters both before and after, so this is not evidence of OCR. Extraction equality alone cannot prove that every PDF viewer will render or copy identically.</p>
<p><a href="assets/all-pages-contact-sheet.png">Inspect the contact sheet of every page</a>. The source and compressed PDFs below let you check text selection and zoom in with your own reader.</p>
<ul><li>Text: <a href="data/text-original.pdf">original</a> / <a href="data/text-compressed.pdf">compressed</a></li><li>Images: <a href="data/images-original.pdf">original</a> / <a href="data/images-compressed.pdf">compressed</a></li><li>Mixed: <a href="data/mixed-original.pdf">original</a> / <a href="data/mixed-compressed.pdf">compressed</a></li></ul></section>
<section id="meaning"><h2>Why the gap is so large here</h2><p>The text PDF was small to begin with and already used compressed content streams. Rewriting and object cleanup saved 636 bytes. That is a real reduction, but it would rarely solve an attachment limit problem.</p>
<p>The two image documents started with losslessly stored, noisy 300-dpi rasters. The pipeline kept only 16% of the pixel count, then applied JPEG, which discards further detail. Their nearly identical savings make sense: they contain the same image payload, while the additional selectable text costs comparatively little.</p>
<p>The 99% figures are strongly dependent on that starting point. An already compressed JPEG scan, a monochrome fax, a document with large embedded fonts, or a signed form could behave differently. This run has no already-JPEG control, no monochrome or font-heavy document, and no signed or tagged PDF. It does not isolate resizing from JPEG encoding, assess accessibility preservation, test printing, or establish a general optimum. Some other inputs or pipelines can produce no saving or a larger output; none of these three did.</p></section>
<section id="choices"><h2>Choose a level, then check what matters</h2><ol><li><strong>Keep the original.</strong> Work on a copy and confirm that an upload limit is the problem you need to solve.</li><li><strong>Look inside the file.</strong> Try selecting body text. Zoom in on scans and diagrams. A page full of pixels responds differently from selectable text.</li><li><strong>Start with moderate settings.</strong> If images are responsible for the size, try a smaller resolution or JPEG quality on a copy. There is no reason to apply this experiment’s 120-dpi setting to every document.</li><li><strong>Inspect the output.</strong> Check every page, small numbers, punctuation, fine lines, and image labels at useful zoom. Copy a sentence and compare it with the original. Confirm page count and file size.</li><li><strong>Choose based on the task.</strong> If tiny labels become hard to read, increase resolution or quality even if the file becomes larger. Keep files with signatures, forms, or accessibility requirements out of an unvalidated rewrite workflow.</li></ol>
<p>For implementation, you can use the local script here or choose a compression interface that exposes the controls you need. Readers who prefer an Arabic walkthrough of online options can consult Idraaak’s guide to <a href="https://idraaak.com/تصغير-حجم-ملف-pdf/" lang="ar" dir="rtl">تصغير حجم ملف PDF</a>. That Arabic article is published by the same publisher as this report; it is a practical companion, not the source of these measurements. We did not test or rank the services it mentions.</p>
<p>For private documents, a local workflow avoids sending the document to an online compressor. This experiment uses only synthetic files, and its code makes no network requests.</p></section>
<section id="sources"><h2>Technical references</h2><ul><li><a href="https://pypdf.readthedocs.io/en/stable/user/file-size.html">pypdf: reducing file size</a> — image replacement, object cleanup, and content-stream compression. The installed version for this run is pinned above.</li><li><a href="https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg">Pillow: JPEG settings</a> — quality and chroma subsampling controls.</li><li><a href="https://github.com/nedal-dev/pdf-compression-lab">Experiment repository</a> — original code, PDF inputs and outputs, raw results, hashes, and actual rendered crops.</li></ul></section>
<footer><p>Publisher: Nedal / Idraaak. Created with AI assistance for code, analysis, visual inspection, and prose; no independent human review is claimed. No affiliation with or endorsement by Posit, pypdf, or Pillow is implied.</p><p>Original code, report text, procedural artwork, and example PDFs are available under the <a href="LICENSE">MIT License</a>. Third-party software retains its own licenses.</p></footer>
</main></body></html>'''
text,images,mixed=d['rows']
replacements={
 '4,532':f"{text['original_bytes']:,}", '3,896':f"{text['compressed_bytes']:,}",
 '14.03%':f"{text['saving_percent']:.2f}%", '636':str(text['original_bytes']-text['compressed_bytes']),
 '14.210':f"{images['original_bytes']/1e6:.3f}", '0.117':f"{images['compressed_bytes']/1e6:.3f}",
 '99.18%':f"{images['saving_percent']:.2f}%", '14.212':f"{mixed['original_bytes']/1e6:.3f}",
 '0.119':f"{mixed['compressed_bytes']/1e6:.3f}", '99.16%':f"{mixed['saving_percent']:.2f}%",
 '7,044':f"{text['original_text_characters']:,}", '2,634':f"{mixed['original_text_characters']:,}",
 'Python 3.12.14':'Python '+d['versions']['python'],
 'Poppler 26.07.0':d['versions']['poppler'].replace('pdftoppm version','Poppler'),
}
for old,new in replacements.items(): html=html.replace(old,new)
html=html.replace('CANONICAL',canonical_tag).replace('ROWS',rows).replace('CHART',chart()).replace('CROPS',crops)
html=html.replace('<svg viewBox=', '<div class="chart-wrap"><svg viewBox=').replace('</svg>', '</svg></div>')
html=html.replace('svg{width:100%;', '.chart-wrap{overflow-x:auto}svg{min-width:680px;width:100%;')
html=html.replace('The upper panel uses kB;', 'On a narrow screen, scroll the chart horizontally. The upper panel uses kB;')
html=html.replace('table{width:100%;','table{min-width:880px;width:100%;')
(ROOT/'index.html').write_text(html,encoding='utf-8')
print('Built static report from recorded results:',len(html),'characters')
