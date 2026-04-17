"""
This script is the pipeline step:

|-----------|            |------------------|
| raw ephys |    --->    | sorting analyzer |
|-----------|            |------------------|

It can be called from the command line. An example:

uv run sort_on_comp.py --mouse 6 --day 12 --sessions OF1,VR,OF2 --protocols kilosort4A --data_folder /home/nolanlab/Work/Harry_Project/data/ --deriv_folder /home/nolanlab/Work/Harry_Project/derivatives/

This will take the ephys data for mouse "6" on day "12" for the three session types "OF1", "VR" and "OF2",
and sort them using protocol "kilosort4A", as described in `nolanlab-ephys/src/nolanlab_ephy/si_protocols.py`.
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

    # Parse the user input

    parser = ArgumentParser()

    parser.add_argument("mouse")
    parser.add_argument("day")
    parser.add_argument("sessions")
    parser.add_argument("protocols")
    parser.add_argument("--data_folder", default="/home/nolanlab/Work/Harry_Project/data/")
    parser.add_argument("--deriv_folder", default="/home/nolanlab/Work/Harry_Project/derivatives/")
    parser.add_argument("--n_jobs", default=8)

    mouse = int(parser.parse_args().mouse)
    day = int(parser.parse_args().day)
    n_jobs = int(parser.parse_args().n_jobs)

    sessions_string = parser.parse_args().sessions
    sessions = sessions_string.split(",")

    protocols = parser.parse_args().protocols
    protocols_list = protocols.split(",")

    data_folder = Path(parser.parse_args().data_folder)
    deriv_folder = Path(parser.parse_args().deriv_folder)

    mouseday_deriv_folder = deriv_folder / f"M{mouse:02d}/D{day:02d}"
    mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day)
    )
    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]

    for protocol in protocols_list:
        analyzer_paths = [
            deriv_folder
            / f"M{mouse:02d}/D{day:02d}/{session}/{protocol}/sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer"
            for session in sessions
        ]

        do_sorting_pipeline_concat_then_split(
            recordings,
            analyzer_paths,
            protocol,
            sorting_output_folder=f"sorting_output_{mouse:02d}_{day:02d}_{protocol}",
            n_jobs=n_jobs,
        )


if __name__ == "__main__":
    main()
