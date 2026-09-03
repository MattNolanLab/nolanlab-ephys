import pandas as pd
from pathlib import Path

data_path = Path("/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Teris/FragileX/")

session_types = ['openfield', 'VR']

# data = []

# for mouse in range(1,11):
#     for day in range(1,50):
#         for session_type in session_types:

#             session_type_folders = [
#                 data_path / "cohort_202108/data" / session_type,
#                 data_path / "data/" / session_type,
#                 data_path / "teris_cohort_202206/data" / session_type,
#             ]
#             for session_type_folder in session_type_folders:
#                 session_folder_list = list(session_type_folder.glob(f'M{mouse}_D{day}_*'))
#                 if len(session_folder_list) > 0:
#                     data.append([mouse, day, session_type, str(Path(*session_folder_list[0].parts[-5:]))])
            
# mouseday_folders = pd.DataFrame(data, columns=["mouse", "day", "session", "filepath"])
# mouseday_folders.to_csv("/home/nolanlab/fromgit/nolanlab-ephys/scripts/teris/resources/all_mouseday_ephys_paths.csv")

mouseday_folders = pd.read_csv("/home/nolanlab/fromgit/nolanlab-ephys/scripts/teris/resources/all_mouseday_ephys_paths.csv")

good_mousedays = {}

for mouse in mouseday_folders['mouse'].unique():
    days = mouseday_folders.query(f'mouse == {mouse}')
    good_days = []
    for day in days['day'].unique():
        if len(mouseday_folders.query(f'mouse == {mouse} & day == {day}')) == 2:
            good_days.append(day)
    good_mousedays[mouse] = good_days


# mouse_days = {
#     1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
#     2: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
#     3: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
#     4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
#     5: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
#     6: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
#     7: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
#     8: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
#     9: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
#     10: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
# }

# good_mouse_days = {}
# for mouse, days in mouse_days.items():
#     good_days = []
#     for day in days:
#         sessions = mouseday_folders.query(f"mouse == {mouse} & day == {day}")['session']
#         if len(sessions) == 2:
#             good_days.append(day)
#     good_mouse_days[mouse] = good_days

# print(good_mouse_days)
        