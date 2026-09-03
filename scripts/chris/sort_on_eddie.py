from eddie_helper.make_scripts import run_python_script
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('protocol')
protocol = parser.parse_args().protocol

protocol = "lupinB"

uv_directory = os.getcwd()
python_arg = f"scripts/chris/sort_ibl_data.py {protocol}"
run_python_script(uv_directory, python_arg, cores=4, email="chalcrow@ed.ac.uk", staging=False, job_name=f"{protocol}_ibl", h_rt="24:00:00")
