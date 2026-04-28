from nolanlab_ephys.utils import chronologize_paths, get_recording_folders, get_session_names
from pathlib import Path
import pandas as pd


active_projects_folder = Path("/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/")
data_folder = active_projects_folder / "Harry/EphysNeuropixelData/"

ephys_days = {
    20: [14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    21: [15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    22: [33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51],
    25: [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    26: [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
    27: [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
    28: [16,17,18,19,20,21,22,23,24,25,26,27,28,29],
    29: [16,17,18,19,20,21,22,23,24,25,26,27,28,29],
}

data = []

for mouse, days in ephys_days.items():
    for day in days:
        recording_folders = chronologize_paths(get_recording_folders(data_folder=data_folder, mouse =mouse, day=day))

        session_names = get_session_names(recording_folders)

        for session_name, recording_folder in zip(session_names, recording_folders):
            recording_folder_from_active = str(recording_folder).split("ActiveProjects/")[1]

            data.append([mouse, day, session_name, recording_folder_from_active])

filepath_df = pd.DataFrame(data, columns=["mouse", "day", "session", "filepath"])