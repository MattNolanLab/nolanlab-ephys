from numpy import record
from eddie_helper.make_scripts import run_python_script, run_stage_script
from argparse import ArgumentParser
from pathlib import Path
from common_paths import  eddie_active_projects, eddie_wolf_data_folder, eddie_wolf_deriv_folder
import os
import pandas as pd
    
parser = ArgumentParser()

parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)

deriv_folder = parser.parse_args().deriv_folder
deriv_folder = Path(deriv_folder)

data_folder = parser.parse_args().data_folder
data_folder = Path(data_folder)

active_projects_path = eddie_active_projects
test_folder = active_projects_path / "Wolf/mmnav/data/test"

folder_names = [
    "M07_TEST_2026-06-06_14-05-13_1",
    "M07_TEST_2026-06-06_14-06-37_2",
    "M07_TEST_2026-06-06_14-07-54_3",
    "M07_TEST_2026-06-06_14-09-13_4",
    "M07_TEST_2026-06-06_14-10-39_5",
    "M07_TEST_2026-06-06_14-11-58_6",
    "M07_TEST_2026-06-06_14-13-17_7",
    "M07_TEST_2026-06-06_14-14-38_8",
    "M07_TEST_2026-06-06_14-16-02_9",
    "M07_TEST_2026-06-06_14-17-29_10",              
    "M07_TEST_2026-06-06_14-18-46_11",
    "M07_TEST_2026-06-06_14-20-08_12",             
    "M07_TEST_2026-06-06_14-21-28_13",
    "M08_TEST_2026-06-06_14-51-03_1",
    "M08_TEST_2026-06-06_14-53-55_2",
    "M08_TEST_2026-06-06_14-55-11_3",
    "M08_TEST_2026-06-06_14-56-26_4",
    "M08_TEST_2026-06-06_14-58-04_5",
    "M08_TEST_2026-06-06_14-59-16_6",
    "M08_TEST_2026-06-06_15-00-29_7",
    "M08_TEST_2026-06-06_15-02-34_8",
    "M08_TEST_2026-06-06_15-04-33_9",
    "M08_TEST_2026-06-06_15-05-44_10",              
    "M08_TEST_2026-06-06_15-07-12_11",             
    "M08_TEST_2026-06-06_15-08-47_12",             
    "M08_TEST_2026-06-06_15-10-02_13",             
    "M09_TEST_2026-06-06_15-37-02_1",
    "M09_TEST_2026-06-06_15-38-12_2",
    "M09_TEST_2026-06-06_15-39-22_3",
    "M09_TEST_2026-06-06_15-40-33_4",
    "M09_TEST_2026-06-06_15-41-51_5",
    "M09_TEST_2026-06-06_15-44-07_6",
    "M09_TEST_2026-06-06_15-45-25_7",
    "M09_TEST_2026-06-06_15-46-34_8",
    "M09_TEST_2026-06-06_15-47-44_9",
    "M09_TEST_2026-06-06_15-48-58_10",              
    "M09_TEST_2026-06-06_15-50-07_11",               
    "M09_TEST_2026-06-06_15-51-16_12",
    "M09_TEST_2026-06-06_15-52-26_13",             
    "M10_TEST_2026-06-06_16-28-18_1",
    "M10_TEST_2026-06-06_16-29-27_2",
    "M10_TEST_2026-06-06_16-30-46_3",
    "M10_TEST_2026-06-06_16-31-58_4",
    "M10_TEST_2026-06-06_16-33-12_5",
    "M10_TEST_2026-06-06_16-34-22_6",
    "M10_TEST_2026-06-06_16-35-38_7",
    "M10_TEST_2026-06-06_16-36-54_8",
    "M10_TEST_2026-06-06_16-38-02_9",
    "M10_TEST_2026-06-06_16-39-15_10",
    "M10_TEST_2026-06-06_16-40-36_11",             
    "M10_TEST_2026-06-06_16-42-01_12",
    "M10_TEST_2026-06-06_16-43-31_13",
]

recording_paths = [
    test_folder / folder_name for folder_name in folder_names
]

uv_directory = os.getcwd()
email = "chalcrow@ed.ac.uk"


for recording_index, recording_path in enumerate(recording_paths):

    stagein_dict = {}

    recording_folder_name = Path(recording_path).name
    session_type_folder = data_folder
    stagein_dict[f"{active_projects_path / recording_path}"] = session_type_folder / recording_folder_name
    session_type_folder.mkdir(exist_ok=True)

    stagein_job_name = f"test_in_{recording_index}" 
    run_python_name = f"test_run_{recording_index}"
    
    python_arg = f"scripts/wolf/test_data/sort_test_data.py --rec_index={recording_index} --data_folder={data_folder} --deriv_folder={deriv_folder}"
    run_stage_script(stagein_dict, job_name=stagein_job_name)
    run_python_script(uv_directory, python_arg, cores=4, email=email, staging=False, hold_jid=stagein_job_name, job_name=run_python_name)
