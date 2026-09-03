import pandas as pd
from pathlib import Path

derivatives_folder = Path("/Volumes/cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Wolf/MMNAV/derivatives")

all_filepaths = pd.read_csv('scripts/wolf/wolf_filepaths.csv')

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


