from eddie_helper.make_scripts import run_python_script, run_stage_script
from argparse import ArgumentParser
from pathlib import Path
from common_paths import  eddie_active_projects, eddie_wolf_data_folder, eddie_wolf_deriv_folder
import os
import pandas as pd
import time

def filepath_from_mouse_day_sessions(mouse, day, sessions, path_to_all_filepaths):
    
    all_filepaths = pd.read_csv(path_to_all_filepaths)
    sessions_filepaths = []
    
    for session in sessions:
        session_column = all_filepaths.query(f'mouse == {mouse} & day == {day} & session == "{session}"')
        filepath = session_column['filepath'].values[0]
        sessions_filepaths.append(filepath)

    return sessions_filepaths
    
parser = ArgumentParser()

parser.add_argument('mice')
parser.add_argument('days')
parser.add_argument('sessions')
parser.add_argument('protocol')
parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)
parser.add_argument('--email', default=None)

mice_string = parser.parse_args().mice
days_string = parser.parse_args().days

mice = mice_string.split(',')
mice = [int(mouse) for mouse in mice]

days = days_string.split(',')
days = [int(day) for day in days]

sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(',')

protocol = parser.parse_args().protocol

data_folder = parser.parse_args().data_folder
if data_folder is None:
    data_folder = eddie_wolf_data_folder
data_folder = Path(data_folder)

if not data_folder.is_dir():
    print(f"Given `data_folder` {data_folder} does not exist.")

deriv_folder = parser.parse_args().deriv_folder
if deriv_folder is None:
    deriv_folder = eddie_wolf_deriv_folder
deriv_folder = Path(deriv_folder)

if not deriv_folder.is_dir():
    print(f"Given `deriv_folder` {deriv_folder} does not exist.")

email = parser.parse_args().email
if email is None:
    email = "chalcrow@ed.ac.uk"

path_to_all_filepaths = "scripts/wolf/wolf_filepaths.csv"

active_projects_path = eddie_active_projects

for mouse in mice:
    for day in days:
            
        recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions=sessions, path_to_all_filepaths=path_to_all_filepaths)
        
        stagein_dict = {}
        for recording_path in recording_paths:
            recording_folder_name = Path(recording_path).name
            if "OF1" in recording_path:
                session_type_folder = data_folder / "OF"
                stagein_dict[f"{active_projects_path / recording_path}"] = session_type_folder
            else:
                session_type_folder = data_folder / "VR"
                stagein_dict[f"{active_projects_path / recording_path}"] = session_type_folder
            session_type_folder.mkdir(exist_ok=True)
        
        stageout_dict = {}
        for session in sessions:
            stageout_dict[deriv_folder / f"M{mouse:02d}/D{day:02d}/{session}/{protocol}"] = eddie_active_projects / "Wolf/MMNAV/derivatives" / f"M{mouse:02d}/D{day:02d}/{session}/"
            stageout_dict[deriv_folder / f"M{mouse:02d}/D{day:02d}/M{mouse:02d}_D{day:02d}_probe_layout.png"] = eddie_active_projects / "Wolf/MMNAV/derivatives" / f"M{mouse:02d}/D{day:02d}/"
        
        stagein_job_name = f"M{mouse}D{day}{sessions[0][:2]}in" 
        run_python_name = f"M{mouse}D{day}{sessions[0][:2]}run"
        quality_name = f"M{mouse}D{day}quality"
        stageout_job_name = f"M{mouse}D{day}{sessions[0][:2]}out" 
        
        uv_directory = os.getcwd()
        python_arg = f"scripts/wolf/sort_on_comp.py {mouse} {day} {sessions_string} {protocol} --data_folder={data_folder} --deriv_folder={deriv_folder}"
        quality_arg = f"scripts/wolf/quality_control.py {mouse} {day} {sessions_string} {protocol} --data_folder={data_folder} --deriv_folder={deriv_folder}"
        
        run_stage_script(stagein_dict, job_name=stagein_job_name)
        run_python_script(uv_directory, python_arg, cores=8, email=email, staging=False, hold_jid=stagein_job_name, job_name=run_python_name)
        time.sleep(2)
        # Do quality control
        run_python_script(uv_directory, quality_arg, cores=8, email=email, staging=False, hold_jid=run_python_name, job_name=quality_name)
        run_stage_script(stageout_dict, job_name=stageout_job_name, hold_jid=run_python_name)
