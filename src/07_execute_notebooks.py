"""Execute all eight notebooks with fresh Jupyter kernels; save only successful runs."""
from pathlib import Path
import json
import os
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT=Path(__file__).resolve().parents[1]


def run():
    records=[]
    with tempfile.TemporaryDirectory(prefix='.jupyter_',dir=ROOT) as temp:
        directory=Path(temp);kernels=directory/'kernels';spec=kernels/'project'
        spec.mkdir(parents=True)
        (spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
                                                  'display_name':'Project Python','language':'python'}))
        os.environ['JUPYTER_RUNTIME_DIR']=str(directory)
        os.environ['IPYTHONDIR']=str(directory/'ipython')
        for path in sorted((ROOT/'notebooks').glob('0*.ipynb')):
            tick=time.perf_counter();print('Executing',path.name,flush=True)
            notebook=nbformat.read(path,as_version=4)
            km=KernelManager(kernel_name='project',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]),
                             connection_file=str(directory/'connection.json'))
            client=NotebookClient(notebook,km=km,timeout=1200,resources={'metadata':{'path':str(ROOT/'notebooks')}})
            try:
                client.execute()
            finally:
                if km.has_kernel:km.shutdown_kernel(now=True)
            errors=[o for c in notebook.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
            if errors:raise AssertionError(f'Execution errors: {path.name}')
            nbformat.write(notebook,path)
            records.append({'notebook':path.name,'code_cells':sum(c.cell_type=='code' for c in notebook.cells),
                            'errors':len(errors),'seconds':round(time.perf_counter()-tick,3)})
            print('PASS',path.name,records[-1]['seconds'],'seconds',flush=True)
    (ROOT/'reports/notebook_execution.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    return records


if __name__=='__main__':run()
