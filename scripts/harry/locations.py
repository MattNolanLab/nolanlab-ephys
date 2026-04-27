from nolanlab_ephys.eddie import filepath_from_mouse_day_sessions, make_and_run_script, make_and_run_locations_script, make_and_run_stageout
from argparse import ArgumentParser
from nolanlab_ephys.common_paths import eddie_active_projects
from pathlib import Path

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('days')
parser.add_argument('sessions')

mouse = int(parser.parse_args().mouse)

days_string = parser.parse_args().days
days_list_string = days_string.split(',')
days = [int(day) for day in days_list_string]

sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(',')

data_folder = Path("/exports/eddie/scratch/chalcrow/harry/data/")
deriv_folder = Path("/exports/eddie/scratch/chalcrow/harry/derivatives/")
active_projects_path = eddie_active_projects

for day in days:

    DS_extensions_path = Path(f"Chris/Cohort12/derivatives/M{mouse}/D{day}/full/kilosort4/kilosort4_sa/extensions/")
    extensions_path = Path(f"M{mouse}/D{day}/full/kilosort4/kilosort4_sa/extensions/")
    locations_path = extensions_path / "spike_locations"

    sa_path = [f"Chris/Cohort12/derivatives/M{mouse}/D{day}/full/kilosort4/kilosort4_sa"]

    destination = Path(deriv_folder) / f"M{mouse}/D{day}/full/kilosort4"
    destination.mkdir(exist_ok=True, parents=True)

    recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions)

    stagein_script_name = f"M{mouse}D{day}_in"
    stagein_sa_script_name = f"M{mouse}D{day}_sain"

    make_and_run_script(active_projects_path, sa_path, destination, stagein_sa_script_name)
    make_and_run_script(active_projects_path, recording_paths, data_folder, stagein_script_name)

    make_and_run_locations_script(mouse, day, wait_for=f" -hold_jid {stagein_script_name}")

    make_and_run_stageout(Path(deriv_folder) / locations_path, active_projects_path, DS_extensions_path, wait_for=f" -hold_jid M{mouse}D{day}loc")