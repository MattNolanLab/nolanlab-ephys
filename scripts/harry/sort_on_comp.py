from argparse import ArgumentParser
from pathlib import Path
from nolanlab_ephys.si_protocols import protocols
from nolanlab_ephys.utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.si_protocols import generic_postprocessing
from nolanlab_ephys.sort import do_sorting_pipeline_concat


import spikeinterface.full as si

def main():

    parser = ArgumentParser()

    parser.add_argument('mouse')
    parser.add_argument('day')
    parser.add_argument('protocol')
    parser.add_argument('--n_jobs', default=8)
    parser.add_argument('--data_folder', default=None)
    parser.add_argument('--deriv_folder', default=None)

    mouse = int(parser.parse_args().mouse)
    day = int(parser.parse_args().day)
    protocol = parser.parse_args().protocol
    n_jobs = parser.parse_args().n_jobs

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = "/home/nolanlab/Work/Harry_Project/data/"
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = "/home/nolanlab/Work/Harry_Project/derivatives/"
    deriv_folder = Path(deriv_folder)

    recording_paths = chronologize_paths(get_recording_folders(data_folder=data_folder, mouse =mouse, day=day))
    print(f"\nWill sort the following recordings:")
    for recording_path in recording_paths:
        print(f"  - {recording_path}")

    analyzer_path = deriv_folder / f"M{mouse}/D{day}/full/sub-{mouse}_day-{day}_srt-{protocol}_analyzer"

    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]

    do_sorting_pipeline_concat(
        recordings,
        analyzer_path,
        protocol,
        n_jobs=n_jobs,
    )


if __name__ == "__main__":
    main()