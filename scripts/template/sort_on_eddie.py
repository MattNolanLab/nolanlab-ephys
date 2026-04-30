"""
This script runs three jobs on EDDIE:

1. Stage in: copy raw data from the DATASTORE to EDDIE scratch
2. Run `sort_on_comp.py` on EDDIE
3. Stage out: copy derived data from the EDDIE scratch to the DATASTORE

Learn more about the sorting script in the docstring of `sort_on_comp.py`.

"""

import os
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd

from eddie_helper.make_scripts import run_python_script, run_stage_script
from common_paths import  eddie_active_projects, eddie_wolf_data_folder, eddie_wolf_deriv_folder

def filepath_from_mouse_day_sessions(mouse, day, sessions, path_to_all_filepaths):
    
    all_filepaths = pd.read_csv(path_to_all_filepaths)
    sessions_filepaths = []
    
    for session in sessions:
        session_column = all_filepaths.query(f'mouse == {mouse} & day == {day} & session == "{session}"')
        filepath = session_column['filepath'].values[0]
        sessions_filepaths.append(filepath)

    return sessions_filepaths

def main():

    parser = ArgumentParser()

    parser.add_argument("mouse")
    parser.add_argument("day")
    parser.add_argument("sessions")
    parser.add_argument("protocol")
    parser.add_argument("--data_folder", default=None)
    parser.add_argument("--deriv_folder", default=None)
    parser.add_argument("--email", default=None)

    mouse = int(parser.parse_args().mouse)
    day = int(parser.parse_args().day)

    sessions_string = parser.parse_args().sessions
    sessions = sessions_string.split(",")

    protocol = parser.parse_args().protocol

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = eddie_wolf_data_folder
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = eddie_wolf_deriv_folder
    deriv_folder = Path(deriv_folder)

    # If you pass your Edinburgh e-mail, you'll get an e-mail after spike sorting has finished.
    email = parser.parse_args().email

    # Need to get the folder we need to stage in to EDDIE, relative to `ActiveProjects`
    # folder. Here, we have saved these in `resources/ephys_filepaths.csv`. The 
    # example data sets are Wolf's data from the MMNAV experiment.
    path_to_all_filepaths = "scripts/wolf/wolf_filepaths.csv"
    recording_paths = filepath_from_mouse_day_sessions(
        mouse, day, sessions=None, path_to_all_filepaths=path_to_all_filepaths
    )
    active_projects_path = eddie_active_projects

    stagein_dict = {}
    for recording_path in recording_paths:
        recording_folder_name = Path(recording_path).name
        stagein_dict[f"{active_projects_path / recording_path}"] = (
            data_folder / recording_folder_name
        )

    stageout_dict = {}
    for session in sessions:
        # the final data will be coped to the DataStore.
        # At the moment they go to "ActiveProjects/Chris/dont_save_stuff_here"
        stageout_dict[deriv_folder / f"M{mouse:02d}/D{day:02d}/{session}/{protocol}"] = (
            eddie_active_projects / "Chris/dont_save_stuff_here"
        )

    stagein_job_name = f"M{mouse}D{day}{sessions[0][:2]}in"
    run_python_name = f"M{mouse}D{day}{sessions[0][:2]}run"
    stageout_job_name = f"M{mouse}D{day}{sessions[0][:2]}out"

    uv_directory = os.getcwd()
    # Run `sort_on_comp.py` with the same parsed arguments.
    python_arg = f"scripts/chris/sort_on_comp.py {mouse} {day} {sessions_string} {protocol} --data_folder={data_folder} --deriv_folder={deriv_folder}"

    run_stage_script(stagein_dict, job_name=stagein_job_name)
    run_python_script(
        uv_directory,
        python_arg,
        cores=8,
        email=email,
        staging=False,
        hold_jid=stagein_job_name,
        job_name=run_python_name,
    )
    run_stage_script(stageout_dict, job_name=stageout_job_name, hold_jid=run_python_name)


if __name__ == "__main__":
    main()
