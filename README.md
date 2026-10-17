# PDF Compression Lab

Original educational report by Nedal / Idraaak. Three synthetic three-page PDFs,
one actually executed local compression pipeline. No private documents or
third-party image assets. AI-assisted code, analysis, visual inspection and prose;
no independent human review is claimed.

## Reproduce

Python 3.12.14, pinned dependencies in `requirements.txt`, Poppler 26.07.0
(`pdftoppm` on PATH). Install these free dependencies in your own environment.

```sh
python -m pip install -r requirements.txt
python experiment.py
python build_report.py
python -m http.server 8765
```

The experiment creates the PDFs in `data/`, renders pages in `assets/`, and writes
byte measurements, exact settings, library versions and SHA-256 hashes to
`data/results.json`. `data/results.csv` contains the table. The original rasters
are deterministic procedural art generated from seed 20261017 + page number.
Text uses PDF base-14 Helvetica. Rendering is Poppler at 144 dpi.

All files have three Letter pages. Images are losslessly stored at 1800x1200,
placed at 432x288 points (300 dpi). The pipeline uses Pillow LANCZOS to resize
them to 720x480 (120 dpi), JPEG quality 75, subsampling 2 (4:2:0), progressive=false,
optimize=false; then pypdf deflate level 9 and identical/unreferenced-object cleanup.
The same pipeline applies to every PDF. Image placement and page geometry remain
unchanged. Extracted text must match exactly on every page; there is no OCR.

These are deliberately synthetic, lossless image inputs, not a representative
sample. The report documents the resulting visual losses and limitations. It
does not compare services or promise a general compression ratio.

## Publish

Deploy `index.html` as a Static Document on Posit Connect Cloud. Keep `robots.txt`
at the published root and enable Public Access. Once the final public URL is
known, save that exact URL in `canonical.txt` and rerun `build_report.py`, then
republish. Verify the anonymous HTML, headers, link, canonical and `/robots.txt`.
No paid service or custom domain is needed. Crawl permission is not indexing.

## License

Original project content is MIT licensed; see LICENSE. Dependencies retain their
respective licenses. The single contextual Arabic link is a publisher-disclosed
companion guide, not the source of the experiment's data.
