from eddie_helper.make_scripts import run_python_script, run_stage_script
from argparse import ArgumentParser
from pathlib import Path
from nolanlab_ephys.eddie import filepath_from_mouse_day_sessions
from nolanlab_ephys.common_paths import  eddie_active_projects, eddie_data_folder, eddie_deriv_folder
import subprocess

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('days')
parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)

mouse = int(parser.parse_args().mouse)

days_string = parser.parse_args().days
days = [int(x) for x in days_string.split(',')]

data_folder = parser.parse_args().data_folder
if data_folder is None:
    data_folder = eddie_data_folder
data_folder = Path(data_folder)

deriv_folder = parser.parse_args().deriv_folder
if deriv_folder is None:
    deriv_folder = eddie_deriv_folder
deriv_folder = Path(deriv_folder)

for day in days:

    recording_paths = filepath_from_mouse_day_sessions(mouse, day)
    active_projects_path = eddie_active_projects

    stagein_dict = {}
    for recording_path in recording_paths:
        stagein_dict[f"{active_projects_path / recording_path}"] = data_folder
    stagein_dict[eddie_active_projects / "Chris/Cohort12/derivatives" / f"M{mouse}/D{day}/full/kilosort4/kilosort4_sa"] = deriv_folder /  f"M{mouse}/D{day}/full/kilosort4/kilosort4_sa"
    subprocess.run(['mkdir', '-p', str(deriv_folder /  f"M{mouse}/D{day}/full/kilosort4/") ])

    stageout_dict = {}
    stageout_dict[deriv_folder / f"M{mouse}/D{day}/full/kilosort4/sub-{mouse}_ses-{day}_srt-kilosort4_full_analyzer.zarr"] = eddie_active_projects / "Chris/Cohort12/derivatives" / f"M{mouse}/D{day}/full/kilosort4/"

    stagein_job_name = f"M{mouse}D{day}in" 
    run_python_name = f"M{mouse}D{day}run"
    stageout_job_name = f"M{mouse}D{day}out" 

    python_arg = f"$HOME/.local/bin/uv run /exports/eddie/scratch/chalcrow/harry/fromgit/nolanlab-ephys/scripts/compute_all_extensions.py {mouse} {day}"

    run_stage_script(stagein_dict, job_name=stagein_job_name)
    run_python_script(python_arg, cores=8, email="chalcrow@ed.ac.uk", staging=False, hold_jid=stagein_job_name, job_name=run_python_name)
    run_stage_script(stageout_dict, job_name=stageout_job_name, hold_jid=run_python_name)