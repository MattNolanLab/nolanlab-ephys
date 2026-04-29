"""
This script is the pipeline step:

|-----------|            |------------------|
| raw ephys |    --->    | sorting analyzer |
|-----------|            |------------------|

It can be called from the command line. An example:

uv run sort_on_comp.py --mouse 6 --day 12 --sessions OF1,VR1,OF2 --protocols kilosort4A --data_folder /home/nolanlab/Work/Harry_Project/data/ --deriv_folder /home/nolanlab/Work/Harry_Project/derivatives/

This will take the ephys data for mouse "6" on day "12" for the three session types "OF1", "VR1" and "OF2",
and sort them using protocol "kilosort4A", as described in `nolanlab-ephys/src/nolanlab_ephy/spikeinterface_tools.py`.
We sort all three sessions together as one, but produce a sorting analyzer for each one.

We expect the data to be stored in the form

data_folder/
    global_session_type/
        M{mouse:02d}_D{day:02d}_*_{session_type}/
            Record Node 109/                        <---- (or whatever openephys spits out)
        M06_D12_blah-blah_OF1/                      <---- example

And the output data will be stored in the form

deriv_folder/
    M{mouse:02d}/
        D{day:02d}/
            probe_layout.pdf
            {session_type}/
                {protocol}/
                    sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer
                    sub-06_day-12_ses-OF1_srt-kilosort4A_analyzer.zarr    <---- example
"""

from argparse import ArgumentParser
from pathlib import Path
import spikeinterface.full as si

from nolanlab_ephys.sort import do_sorting_pipeline_concat_then_split
from nolanlab_ephys.utils import get_recording_folders, chronologize_paths


def main():

    parsed_args = get_args()

    mouse = parsed_args.mouse
    if mouse.isdigit():
        mouse = int(mouse)

    day = parsed_args.day
    if day.isdigit():
        day = int(day)

    n_jobs = parsed_args.n_jobs
    protocol = parsed_args.protocol

    sessions_string = parsed_args.sessions
    sessions = sessions_string.split(",")

    data_folder = Path(parsed_args.data_folder)
    deriv_folder = Path(parsed_args.deriv_folder)

    if not data_folder.is_dir():
        raise FileNotFoundError(f"`data_folder` {data_folder} does not exist, or is not mounted.")

    if not deriv_folder.is_dir():
        raise FileNotFoundError(f"`deriv_folder` {deriv_folder} does not exist, or is not mounted.")

    mouseday_deriv_folder = deriv_folder / f"M{mouse}/D{day}"
    mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day, sessions=sessions)
    )
    print(f"\nWill sort the following recordings:")
    for recording_path in recording_paths:
        print(f"  - {recording_path}")

    analyzer_paths = [
        deriv_folder
        / f"M{mouse}/D{day}/{session}/{protocol}/sub-{mouse}_day-{day}_ses-{session}_srt-{protocol}_analyzer"
        for session in sessions
    ]

    print(f"\nAnd save the output at:")
    for analyzer_path in analyzer_paths:
        print(f"  - {analyzer_path}")
    print()

    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]

    do_sorting_pipeline_concat_then_split(
        recordings,
        analyzer_paths,
        protocol=protocol,
        sorting_output_folder=f"sorting_output_{mouse}_{day}_{protocol}",
        n_jobs=n_jobs,
    )

def get_args():

    parser = ArgumentParser()

    parser.add_argument("mouse")
    parser.add_argument("day")
    parser.add_argument("sessions")
    parser.add_argument("protocol")
    parser.add_argument("--data_folder", default="/home/nolanlab/Work/Harry_Project/data/")
    parser.add_argument("--deriv_folder", default="/home/nolanlab/Work/Harry_Project/derivatives/")
    parser.add_argument("--n_jobs", default=8)

    return parser.parse_args()


if __name__ == "__main__":
    main()
