from pathlib import Path
import os
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
root=Path(__file__).resolve().parent
os.chdir(root)
os.environ['MPLCONFIGDIR']=str(root/'.matplotlib')
shell=InteractiveShell.instance()
import matplotlib
matplotlib.use('module://matplotlib_inline.backend_inline')
from matplotlib_inline.backend_inline import configure_inline_support
configure_inline_support(shell, 'inline')
n=nbformat.read(root/'cviceni.ipynb',as_version=4)
count=0
for i,c in enumerate(n.cells):
    if c.cell_type!='code': continue
    count+=1
    print('Cell',i,flush=True)
    with capture_output() as cap:
        result=shell.run_cell(c.source,store_history=True)
    c.execution_count=count
    outputs=[]
    if cap.stdout: outputs.append(nbformat.v4.new_output('stream',name='stdout',text=cap.stdout))
    if cap.stderr: outputs.append(nbformat.v4.new_output('stream',name='stderr',text=cap.stderr))
    for out in cap.outputs:
        outputs.append(nbformat.v4.new_output('display_data',data=out.data,metadata=out.metadata))
    c.outputs=outputs
    nbformat.write(n,root/'cviceni.ipynb')
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f'Cell {i}: {result.error_before_exec or result.error_in_exec}')
nbformat.validate(n)
print('SUCCESS',count,flush=True)

