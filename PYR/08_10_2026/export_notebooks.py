"""Export the current, user-edited notebooks without overwriting or executing them."""
from pathlib import Path
import hashlib
import json
import zipfile
import build_reports

root = Path(__file__).resolve().parent
original_hashes = {}
for lang in ['Python', 'R']:
    path = root / f'Radimsky {lang}.ipynb'
    original_hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
    notebook = json.loads(path.read_text(encoding='utf-8'))
    normalized = []
    for cell in notebook['cells']:
        cell = dict(cell)
        if isinstance(cell['source'], list):
            cell['source'] = ''.join(cell['source'])
        if cell['cell_type'] == 'code':
            output_text = []
            for output in cell.get('outputs', []):
                if output['output_type'] == 'error':
                    raise ValueError(f'{lang}: saved execution error in cell {cell.get("execution_count")}')
                text = output.get('text', output.get('data', {}).get('text/plain', ''))
                output_text.append(''.join(text) if isinstance(text, list) else text)
            cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout',
                                'text': '\n'.join(output_text)}]
        normalized.append(cell)
    build_reports.cells[lang] = normalized
    build_reports.render_pdf(lang)
with zipfile.ZipFile(root / 'Radimsky Lab02.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for lang in ['Python', 'R']:
        path = root / f'Radimsky {lang}.pdf'
        archive.write(path, path.name)
for path, original in original_hashes.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == original
print('Exported current notebook contents. Both edited notebooks are unchanged.')
