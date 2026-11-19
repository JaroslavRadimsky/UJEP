import json,io,contextlib,base64,traceback
from pathlib import Path
p=Path('05_11_2026/Radimsky_R_vizualizace.ipynb'); nb=json.loads(p.read_text(encoding='utf-8')); ns={}; count=0
for c in nb['cells']:
 if c['cell_type']!='code':continue
 count+=1; outputs=[]; stream=io.StringIO()
 def show(obj):
  outputs.append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(obj.data).decode(),'text/plain':['<R plot>']}})
 try:
  with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
   exec(''.join(c['source']),ns)
  ns['display']=show
 except Exception:
  print('ERROR',count);print(traceback.format_exc());print(stream.getvalue());raise
 c['execution_count']=count
 c['outputs']=([{'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(True)}] if stream.getvalue() else [])+outputs
 print('OK',count)
nb['metadata']['language_info']['version']=ns['sys'].version.split()[0]
p.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
print('Saved executed notebook')
