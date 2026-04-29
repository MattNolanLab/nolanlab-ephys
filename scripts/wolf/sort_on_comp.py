from argparse import ArgumentParser
from pathlib import Path
from nolanlab_ephys.utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.sort import do_sorting_pipeline_concat_then_split

import spikeinterface.full as si

def main():

    parser = ArgumentParser()

    parser.add_argument('mouse')
    parser.add_argument('day')
    parser.add_argument('sessions')
    parser.add_argument('protocols')
    parser.add_argument('--data_folder', default=None)
    parser.add_argument('--deriv_folder', default=None)

    mouse = int(parser.parse_args().mouse)
    day = int(parser.parse_args().day)

    sessions_string = parser.parse_args().sessions
    sessions = sessions_string.split(',')

    protocols_string = parser.parse_args().protocols
    protocols_list = protocols_string.split(',')

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = "/home/nolanlab/Work/Harry_Project/data/VR/"
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = "/home/nolanlab/Work/Harry_Project/derivatives/"
    deriv_folder = Path(deriv_folder)

    mouseday_deriv_folder = deriv_folder / f"M{mouse:02d}/D{day:02d}"
    mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day, sessions=sessions)
    )
    print(f"\nWill sort the following recordings:")
    for recording_path in recording_paths:
        print(f"  - {recording_path}")

    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]

    for protocol in protocols_list:

        analyzer_paths = [
            mouseday_deriv_folder / f"{session}/{protocol}/sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer"
            for session in sessions
        ]

        do_sorting_pipeline_concat_then_split(
            recordings,
            analyzer_paths,
            protocol,
            sorting_output_folder=f"sorting_output_{mouse}_{day}_{protocol}",
            n_jobs=8,
        )


if __name__ == "__main__":
    main()
