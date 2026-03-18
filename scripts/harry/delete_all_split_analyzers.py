from nolanlab_ephys.common_paths import eddie_active_projects

from pathlib import Path

deriv_folder = Path(eddie_active_projects) / 'Chris/Cohort12/derivatives/'

of_days = {
    20: [14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    21: [15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    22: [33,34,35,36,37,38,39,40,41],
    25: [16,17,18,19,21,20,22,23,24,25],
    26: [11,12,13,14,15,16,17,18,19],
    27: [16,17,18,19,20,21,22,23,24,26],
    28: [16,17,18,19,20,21,22,23,25],
    29: [16,17,18,19,20,21,22,23,25]
}

typs = ['OF1', 'VR', 'OF2']

for mouse, days in of_days.items():
    for day in days:
        for typ in typs:
            analyzer_folder = deriv_folder / f'M{mouse}/D{day}/{typ.lower()}/sub-M{mouse}_ses-D{day}_typ-{typ}_srt-kilosort4_analyzer.zarr'
            print(f"rm -r {analyzer_folder}")
