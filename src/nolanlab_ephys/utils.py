"""
Some utility functions.
"""

import os
from pathlib import Path
import numpy as np
import spikeinterface.full as si


def get_chrono_concat_recording(data_folder, mouse, day, sessions=None):

    recording_folders = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day, sessions=sessions)
    )

    mouseday_recording_folders = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day)
    )

    session_names = get_session_names(mouseday_recording_folders)

    if sessions is not None:
        included_sessions = [session_name in sessions for session_name in session_names]
        recording_folders = np.array(mouseday_recording_folders)[np.array(included_sessions)]
    else:
        recording_folders = np.array(mouseday_recording_folders)

    if mouse in (20, 21):
        recordings = [
            si.read_zarr(Path(recording_folder) / "recording.zarr")
            for recording_folder in recording_folders
        ]
    else:
        recordings = [si.read_openephys(recording_folder) for recording_folder in recording_folders]

    recording = si.concatenate_recordings(recordings)

    return recording


def get_recording_folders(data_folder, mouse, day, sessions=None):
    """

    This function expects raw data to be in the format:

    data_folder/
        {session_type}/
            M{mouse}_D{day}_date-time/
                (which might contain openephys, or `recording.zarr` files)
            M{mouse}_D{day}_date-time/
        {another session type}/
        ...

    or

    data_folder/
        M{mouse}_D{day}_date-time/
            (which might contain openephys, or `recording.zarr` files)
        M{mouse}_D{day}_date-time/
            {another session type}/

    or

    data_folder/
        {mouse}/
            {mouse}_{date}*/

    This function returns the recording folders. It also deals with the case if you
    have a extra /data directory. This is often not used for
    the raw data but is used when processing.
    """

    recording_folders = []
    data_path = data_folder

    sessions = [
        "of",
        "vr",
        "openfield",
        "openfieldcd",
        "vr_multi_context",
        "allen_brain_observatory_visual_sequences",
        "allen_brain_observatory_visual_multi_sequences",
        "allen_brain_observatory_visual_coding",
        "dvd_waitscreen",
    ]

    try_both_mousestrings = False
    if isinstance(mouse, int):
        mouse_string = f"M{mouse:02d}"
        mouse_string_2 = f"M{mouse}"
        if mouse_string != mouse_string_2:
            try_both_mousestrings = True
    else:
        mouse_string = mouse

    try_both_daystrings = False
    if isinstance(day, int):
        day_string = f"D{day:02d}"
        day_string_2 = f"D{day}"
        if day_string != day_string_2:
            try_both_daystrings = True
    else:
        day_string = day

    subfolder_to_look_in = []

    # Bri's recordings are ordered by mouse id
    folders_called_mousename_in_data_folder = list(Path(data_path).glob(mouse_string))
    if len(folders_called_mousename_in_data_folder) > 0:
        subfolder_to_look_in = folders_called_mousename_in_data_folder

    # Harry, Wolf recordings are ordered by mouse id
    folders_called_session_in_data_folder = []
    for session_type in sessions:
        folders_called_session_in_data_folder = folders_called_session_in_data_folder + list(
            Path(data_path).glob(session_type)
        )

    if len(folders_called_session_in_data_folder) > 0:
        subfolder_to_look_in = subfolder_to_look_in + folders_called_session_in_data_folder

    recording_folders = []
    
    for subfolder in subfolder_to_look_in:
        recording_folders += list(Path(subfolder).glob(f"{mouse_string}_{day_string}*"))
        if try_both_daystrings:
            recording_folders += list(Path(subfolder).glob(f"{mouse_string}_{day_string_2}*"))
        if try_both_mousestrings:
            recording_folders += list(Path(subfolder).glob(f"{mouse_string_2}_{day_string}*"))
        if try_both_daystrings and try_both_mousestrings:
            recording_folders += list(Path(subfolder).glob(f"{mouse_string_2}_{day_string_2}*"))

    return recording_folders


def get_session_names(raw_recording_paths):
    """
    Returns the session types from a list of raw recording paths
    """

    # This dictionary maps the session names we use to the different
    # naming conventions the experimenter used during the experiment.
    session_naming_dict = {
        "OF1": ["OF1"],
        "OF2": ["OF2"],
        "VR": ["VR1"],
        "MCVR": ["MCVR1", "MCVR", "VRMC"],
        "IM": ["IM", "IM1", "VID1", "VIS1"],
        "IMSEQ": ["IMSEQ"],
        "IMSEQ2": ["IMSEQ2"],
        "DVD": ["DVD", "HDDVD"],
    }

    session_names = []
    for recording_path in raw_recording_paths:
        got_session_type = False
        end_of_name = str(recording_path).split("_")[-1]
        for our_label, exp_label in session_naming_dict.items():
            if end_of_name in exp_label:
                session_names.append(our_label)
                got_session_type = True

        if not got_session_type:
            raise Exception("Don't know session type")

    return session_names


def this_is_zarr(recording_folder):
    """
    Checks if a recording_folder is zarr or not.
    Zarr and open_ephys recording are loaded in different ways
    in spikeinterface.
    """

    zarr_recording = False
    if ".zarr" in str(recording_folder) or len(list(Path(recording_folder).rglob("*.zarr/"))) > 0:
        zarr_recording = True

    return zarr_recording


def get_recording_from(recording_folder):

    if this_is_zarr(recording_folder):
        if ".zarr" not in str(recording_folder):
            recording_folder = Path(recording_folder) / Path("recording.zarr")
        recording = si.load_extractor(recording_folder)
    else:
        recording = si.read_openephys(recording_folder / Path("Record Node 109"))

    return recording


def get_recordings_from(recording_folders):

    recordings = []
    for recording_folder in recording_folders:
        recordings.append(get_recording_from(recording_folder))

    return recordings


def chronologize_paths(recording_paths):
    """
    For a given set of paths, put them in chronological order
    """
    # get basenames of the recordings
    basenames = [os.path.basename(s) for s in recording_paths]
    # split the basename by the first "-" and take only the latter split
    time_dates = [s.split("-", 1)[-1] for s in basenames]
    # reorganise recording_paths based on np.argsort(time_dates)
    recording_paths = np.array(recording_paths)[np.argsort(time_dates)]
    return recording_paths.tolist()
