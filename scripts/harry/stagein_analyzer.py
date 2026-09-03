from nolanlab_ephys.eddie import make_and_run_script
from argparse import ArgumentParser
from nolanlab_ephys.common_paths import eddie_active_projects, chris_linux_active_projects
from pathlib import Path

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')
parser.add_argument('derivatives')

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)
derivatives = parser.parse_args().derivatives

sa_path = [f"Chris/Cohort12/derivatives/M{mouse}/D{day}/full/kilosort4/kilosort4_sa"]

active_projects_path = eddie_active_projects

destination = Path(derivatives) / f"M{mouse}/D{day}/full/kilosort4"
destination.mkdir(exist_ok=True, parents=True)

make_and_run_script(active_projects_path, sa_path, destination)
