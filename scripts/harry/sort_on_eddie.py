from eddie_helper.make_scripts import run_python_script, run_stage_script
from argparse import ArgumentParser
from pathlib import Path
from nolanlab_ephys.eddie import filepath_from_mouse_day_sessions
from nolanlab_ephys.common_paths import  eddie_active_projects, eddie_harry_deriv_folder, eddie_harry_data_folder
import os

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')
parser.add_argument('sessions')
parser.add_argument('protocol')
parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)
parser.add_argument('--email', default=None)

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)

sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(',')

protocol = parser.parse_args().protocol

data_folder = parser.parse_args().data_folder
if data_folder is None:
    data_folder = eddie_harry_data_folder
data_folder = Path(eddie_harry_data_folder)

deriv_folder = parser.parse_args().deriv_folder
if deriv_folder is None:
    deriv_folder = eddie_harry_deriv_folder
deriv_folder = Path(eddie_harry_deriv_folder)

email = parser.parse_args().email
if email is None:
    email = "chalcrow@ed.ac.uk"

path_to_all_filepaths = "scripts/harry/harry_filepaths.csv"
recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions=None, path_to_all_filepaths=path_to_all_filepaths)
active_projects_path = eddie_active_projects

stagein_dict = {}
for recording_path in recording_paths:
    stagein_dict[f"{active_projects_path / recording_path}"] = data_folder

stageout_dict = {}
stageout_dict[deriv_folder / f"M{mouse}/D{day}/{''.join(sessions)}/"] = eddie_active_projects / "Chris/Cohort12/derivatives" / f"M{mouse}/D{day}/"

stagein_job_name = f"M{mouse}D{day}{sessions[0]}in" 
run_python_name = f"M{mouse}D{day}{sessions[0]}run"
stageout_job_name = f"M{mouse}D{day}{sessions[0]}out" 

uv_directory = os.getcwd()
python_arg = f"scripts/harry/sort_on_comp.py {mouse} {day} {sessions_string} {protocol} --data_folder={data_folder} --deriv_folder={deriv_folder}"

run_stage_script(stagein_dict, job_name=stagein_job_name)
run_python_script(uv_directory, python_arg, cores=8, email=email, staging=False, hold_jid=stagein_job_name, job_name=run_python_name)
run_stage_script(stageout_dict, job_name=stageout_job_name, hold_jid=run_python_name)