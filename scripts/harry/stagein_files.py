from nolanlab_ephys.eddie import filepath_from_mouse_day_sessions, make_and_run_script
from argparse import ArgumentParser
from nolanlab_ephys.common_paths import eddie_active_projects

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')
parser.add_argument('sessions')
parser.add_argument('destination')

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)
sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(',')
destination = parser.parse_args().destination

recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions)

active_projects_path = eddie_active_projects

stagein_script_name = f"M{mouse}D{day}_in"
script_name = make_and_run_script(active_projects_path, recording_paths, destination, stagein_script_name)



