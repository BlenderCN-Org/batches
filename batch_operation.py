from subprocess import run as _
from pathlib import Path as _p

def gmic_batch_op(gmic_exe_path,gmic_command_string,inputdir,outputdir,file_ext=".png"):
    print("vars:",vars)
    for fpath in _p(inputdir).glob("*"+file_ext):
        print(fpath.name)
        _([gmic_exe_path,str(fpath)]+gmic_command_string.split()+[str(_p(outputdir)/fpath.name)])
