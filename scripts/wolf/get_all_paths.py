from argparse import ArgumentParser
from pathlib import Path
import pandas as pd

parser = ArgumentParser()
parser.add_argument('--data_folder', default=None)

data_folder = parser.parse_args().data_folder
if data_folder is None:
    data_folder = "/Volumes/cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Wolf/MMNAV/raw"
data_folder = Path(data_folder)

session_types = ['OF', 'VR']

recording_folders = []
for session_type in session_types:
    recording_folders += list(Path(data_folder).glob(f"{session_type}/M*_D*"))

data = []
for recording_folder in recording_folders:
    
    recording_name = recording_folder.name
    mouse = int(recording_name[1:3])
    day = int(recording_name[5:7])
    session = recording_name.split('_')[-1]
    path_from_active = '/'.join(recording_folder.parts[-5:])
    
    data.append( [mouse, day, session, path_from_active] )

all_filepaths = pd.DataFrame(data, columns=["mouse", "day", "session", "filepath"])
all_filepaths.to_csv("scripts/wolf/wolf_filepaths.csv", index=False)

derivatives_folder = Path("/Volumes/cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Wolf/MMNAV/derivatives")

for _, row in all_filepaths.iterrows():
    
    mouse = row['mouse']
    day = row['day']
    session = row['session']
    filepath = row['filepath']

    print(f'mouse {mouse} day {day} session {session}')

    mousedaysession_folder = derivatives_folder / f'M{mouse:02d}' / f'D{day:02d}' / f'{session}'

    mousedaysession_folder.parent.parent.mkdir(exist_ok=True)
    mousedaysession_folder.parent.mkdir(exist_ok=True)
    mousedaysession_folder.mkdir(exist_ok=True)
