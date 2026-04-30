"""
This script creates some quality control plots from raw Neuropixels ephys data.

It can be called from the command line. An example:

uv run quality_control.py --mouse 6 --day 12 --sessions OF1,VR,OF2 --data_folder /home/nolanlab/Work/Harry_Project/data/ --deriv_folder /home/nolanlab/Work/Harry_Project/derivatives/

Computes and plots:
  - noise-vs-channel across time
  - estimated noise vector
  - drift map

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
                recording_quality_plots/
                    sub-{mouse:02d}_day-{day:02d}_typ-{session}_noise_across_time.png
                    sub-{mouse:02d}_day-{day:02d}_typ-{session}_motion_vector.png
                    sub-{mouse:02d}_day-{day:02d}_typ-{session}_drift_map.png
                    sub-{mouse:02d}_day-{day:02d}_typ-{session}_depth_analysis.png
"""

from argparse import ArgumentParser
from pathlib import Path

import spikeinterface.full as si

from nolanlab_ephys.lab_utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.np_quality_control import (
    compute_noise_across_time,
    plot_noise_across_time,
    plot_motion_vector,
    plot_drift_map,
    compute_noise_and_good_units,
    plot_noise_and_good_units,
)


def main():

    parsed_args = get_args()

    mouse = parsed_args.mouse
    day = parsed_args.day

    mouse_string = f"{mouse:02d}"
    day_string = f"{day:02d}"

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

    if not mouseday_deriv_folder.is_dir():
        raise FileNotFoundError(
            f"mouseday_deriv_folder {mouseday_deriv_folder} does not exist, or is not mounted."
        )

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day, sessions=sessions)
    )

    analyzer_paths = [
        deriv_folder
        / mouseday_deriv_folder
        / f"{session}/{protocol}/sub-{mouse_string}_day-{day_string}_ses-{session}_srt-{protocol}_analyzer.zarr"
        for session in sessions
    ]

    if len(recording_paths) != len(analyzer_paths):
        raise ValueError("length of `recording_paths` not equal to length of `analyzer_paths`")

    for session, recording_path, analyzer_path in zip(
        sessions, recording_paths, analyzer_paths, strict=True
    ):
        recording = si.read_openephys(recording_path)
        pp_recording = si.depth_order(si.bandpass_filter(si.common_reference(recording)))
        analyzer = si.load_sorting_analyzer(analyzer_path)

        quality_plots_folder = (
            mouseday_deriv_folder / f"{session}/{protocol}/recording_quality_plots/"
        )
        quality_plots_folder.mkdir(parents=True, exist_ok=True)

        # noise across time
        noise_across_time_filename = (
            quality_plots_folder
            / f"sub-{mouse_string}_day-{day_string}_type-{session}_noise_across_time.png"
        )
        channel_noise_per_minute = compute_noise_across_time(pp_recording)
        plot_noise_across_time(channel_noise_per_minute, noise_across_time_filename)

        # motion across time
        motion_vector_filename = (
            quality_plots_folder
            / f"sub-{mouse_string}_day-{day_string}_type-{session}_motion_vector.png"
        )
        drift_map_filename = (
            quality_plots_folder
            / f"sub-{mouse_string}_day-{day_string}_type-{session}_drift_map.png"
        )
        motion, motion_info = si.compute_motion(
            pp_recording,
            preset="nonrigid_fast_and_accurate",
            estimate_motion_kwargs={"conv_engine": "numpy"},
            output_motion_info=True,
        )
        plot_motion_vector(motion, motion_vector_filename)
        plot_drift_map(motion_info, drift_map_filename)

        # noise and good units along probe
        noise_and_good_units_filename = (
            quality_plots_folder
            / f"sub-{mouse_string}_day-{day_string}_type-{session}_noise_and_good_units.png"
        )
        unique_shanks, noise_per_shank, y_locs_per_shank, mua_per_shank, good_per_shank = (
            compute_noise_and_good_units(analyzer)
        )
        plot_noise_and_good_units(
            unique_shanks,
            noise_per_shank,
            y_locs_per_shank,
            mua_per_shank,
            good_per_shank,
            noise_and_good_units_filename,
        )


def get_args():

    parser = ArgumentParser()

    parser.add_argument("mouse", type=int)
    parser.add_argument("day", type=int)
    parser.add_argument("sessions")
    parser.add_argument("protocol")
    parser.add_argument("--data_folder", default="/home/nolanlab/Work/Harry_Project/data/")
    parser.add_argument("--deriv_folder", default="/home/nolanlab/Work/Harry_Project/derivatives/")

    return parser.parse_args()


if __name__ == "__main__":
    main()
