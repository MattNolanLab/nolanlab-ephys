from nolanlab_ephys.eddie import filepath_from_mouse_day_sessions
from argparse import ArgumentParser
from nolanlab_ephys.common_paths import chris_linux_active_projects, eddie_active_projects
from pathlib import Path
from subprocess import run

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')
parser.add_argument('sessions')
parser.add_argument('--destination', default=None)

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)
sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(',')

destination = parser.parse_args().destination
if destination is None:
    destination = Path("/home/nolanlab/Work/Harry_Project/data/")

recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions)

active_projects_path = eddie_active_projects

for recording_path in recording_paths:
    run(["cp", "-r", f"{active_projects_path / recording_path}", f"{destination}"])