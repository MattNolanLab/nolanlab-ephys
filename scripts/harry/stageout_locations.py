from nolanlab_ephys.eddie import make_and_run_stageout
from argparse import ArgumentParser
from nolanlab_ephys.common_paths import eddie_active_projects
from pathlib import Path

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')
parser.add_argument('derivatives')

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)
derivatives = parser.parse_args().derivatives

DS_extensions_path = Path(f"Chris/Cohort12/derivatives/M{mouse}/D{day}/full/kilosort4/kilosort4_sa/extensions/")
extensions_path = Path(f"M{mouse}/D{day}/full/kilosort4/kilosort4_sa/extensions/")
locations_path = extensions_path / "spike_locations"

active_projects_path = eddie_active_projects

make_and_run_stageout(Path(derivatives) / locations_path, active_projects_path, DS_extensions_path)
