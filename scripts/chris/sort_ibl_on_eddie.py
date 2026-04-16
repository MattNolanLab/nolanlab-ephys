from eddie_helper.make_scripts import run_python_script
from argparse import ArgumentParser
import os

parser = ArgumentParser()

parser.add_argument('protocol')

protocol = parser.parse_args().protocol

email = "chalcrow@ed.ac.uk"

uv_directory = os.getcwd()
python_arg = f"scripts/chris/sort_ibl_data.py {protocol}"

run_python_script(uv_directory, python_arg, cores=8, email=email, staging=False, job_name=protocol)
