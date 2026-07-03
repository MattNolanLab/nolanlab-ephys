import os
from eddie_helper.make_scripts import run_python_script, run_stage_script, run_stagein_script
from argparse import ArgumentParser
from pathlib import Path
import subprocess
import pandas as pd

eddie_active_projects = Path("/exports/cmvm/datastore/sbms/groups/INCR-NolanLab/ActiveProjects")

def filepath_from_mouse_day_sessions(mouse, day, path_to_all_filepaths):
    
    all_filepaths = pd.read_csv(path_to_all_filepaths)
    sessions_filepaths = []
    

    session_column = all_filepaths.query(f'mouse == {mouse} & day == {day}"')
    filepath = session_column['filepath'].values[0]
    sessions_filepaths.append(filepath)

    return sessions_filepaths


parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('days')
parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)

mouse = int(parser.parse_args().mouse)

days_string = parser.parse_args().days
days = [int(x) for x in days_string.split(',')]

data_folder = Path(parser.parse_args().data_folder)
deriv_folder = Path(parser.parse_args().deriv_folder)

for day in days:

    rec_samples = pd.read_csv("scripts/harry/resources/all_rec_samples_involving_mcvr.csv")
    recording_paths = filepath_from_mouse_day_sessions(mouse, day, "scripts/harry/harry_filepaths.csv")

    stagein_dict = {}
    for recording_path in recording_paths:
        stagein_dict[f"{eddie_active_projects / recording_path}"] = data_folder
    stagein_dict[eddie_active_projects / "Chris/Cohort12/derivatives" / f"M{mouse}/D{day}/full/kilosort4/sub-{mouse}_ses-{day}_srt-kilosort4_full_analyzer.zarr"] = deriv_folder /  f"M{mouse}/D{day}/full/kilosort4/"
    subprocess.run(['mkdir', '-p', str(deriv_folder /  f"M{mouse}/D{day}/full/kilosort4/") ])
    
    stagein_job_name = f"M{mouse}D{day}in" 
    run_python_name = f"M{mouse}D{day}run"

    uv_directory = os.getcwd()
    python_arg = f"$HOME/.local/bin/uv run --no-sync /exports/eddie/scratch/chalcrow/harry/code/nolanlab-ephys/scripts/harry/recompute_extensions.py {mouse} {day}"

    run_stagein_script(stagein_dict, job_name=stagein_job_name)
    run_python_script(uv_directory, python_arg, cores=8, email="chalcrow@ed.ac.uk", staging=False, hold_jid=stagein_job_name, job_name=run_python_name)
