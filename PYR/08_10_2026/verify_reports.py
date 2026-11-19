from pathlib import Path
import json
import zipfile
import pdfplumber
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw

root = Path(__file__).resolve().parent
tmp = root / 'tmp' / 'pdfs'
thumbnails = []
for lang in ['Python', 'R']:
    path = root / f'Radimsky {lang}.pdf'
    with pdfplumber.open(path) as doc:
        text = '\n'.join(page.extract_text() or '' for page in doc.pages)
        for part in range(1, 6):
            assert f'Part {part}' in text
        assert '114' in text and '67' in text and '127' in text
        assert 'PASS:' in text
        for number, page in enumerate(doc.pages, 1):
            for char in page.chars:
                assert 30 <= char['x0'] < char['x1'] <= page.width - 30, (lang, number, char)
                assert 25 <= char['top'] < char['bottom'] <= page.height - 12, (lang, number, char)
        print(lang, 'pages:', len(doc.pages), 'text and page bounds PASS')
    rendered = pdfium.PdfDocument(str(path))
    for number in range(len(rendered)):
        pic = rendered[number].render(scale=1.2).to_pil().convert('RGB')
        pic.save(tmp / f'{lang}_page_{number + 1:02d}.png')
        thumb = ImageOps.contain(pic, (298, 421))
        tile = Image.new('RGB', (318, 455), 'white')
        tile.paste(thumb, (10, 25))
        ImageDraw.Draw(tile).text((10, 5), f'{lang} page {number+1}', fill='black')
        thumbnails.append(tile)
    nb = json.loads((root / f'Radimsky {lang}.ipynb').read_text(encoding='utf-8'))
    code = [c for c in nb['cells'] if c['cell_type'] == 'code']
    assert [c['execution_count'] for c in code] == list(range(1, len(code)+1))
    assert all(c['outputs'] and c['outputs'][0]['output_type'] == 'stream' for c in code)
    assert not any(o.get('output_type') == 'error' for c in code for o in c['outputs'])
    print(lang, 'executed notebook cells:', len(code))
cols = 4
rows = (len(thumbnails) + cols - 1) // cols
sheet = Image.new('RGB', (cols * 318, rows * 455), '#ccd3da')
for i, tile in enumerate(thumbnails):
    sheet.paste(tile, ((i % cols)*318, (i//cols)*455))
sheet.save(tmp / 'contact_sheet.png')
with zipfile.ZipFile(root / 'Radimsky Lab02.zip') as archive:
    assert sorted(archive.namelist()) == ['Radimsky Python.pdf', 'Radimsky R.pdf']
    assert archive.testzip() is None
print('ZIP PASS: exactly two PDFs and no corrupt entries')
