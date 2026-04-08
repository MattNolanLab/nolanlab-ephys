import os
from pathlib import Path
import numpy as np
import spikeinterface.full as si


def get_recording_folders(data_folder, mouse, day):
    """

    This function expects raw data to be in the format:

    data_folder/
        {session_type}/
            M{mouse}_D{day}_date-time/
                (which might contain openephys, or `recording.zarr` files)
            M{mouse}_D{day}_date-time/
        {another session type}/
        ...


    This function returns the recording folders. It also deals with the case if you
    have a extra /data directory. This is often not used for
    the raw data but is used when processing.
    """

    recording_folders = []
    data_path = data_folder
    if len(list(Path(data_folder).glob("data/"))) > 0:
        data_path += "data/"

    session_types = [
        "OF",
        "VR",
        "of",
        "vr",
        "vr_multi_context",
        "allen_brain_observatory_visual_sequences",
        "allen_brain_observatory_visual_multi_sequences",
        "allen_brain_observatory_visual_coding",
        "dvd_waitscreen",
    ]

    recording_folders = []
    for session_type in session_types:
        recording_folders += list(Path(data_path).glob(f"{session_type}/M{mouse:02d}_D{day:02d}*"))

    for a, recording_folder in enumerate(recording_folders):
        recording_folders[a] = str(recording_folder)

    return recording_folders


def get_session_names(raw_recording_paths):
    """
    Returns the session types from a list of raw recording paths
    """

    # This dictionary maps the session names we use to the different
    # naming conventions the experimenter used during the experiment.
    session_naming_dict = {
        "of1": ["OF1"],
        "of2": ["OF2"],
        "vr": ["VR1"],
        "vr_multi_context": ["MCVR1", "MCVR", "VRMC"],
        "allen_brain_observatory_visual_coding": ["IM", "IM1", "VID1", "VIS1"],
        "allen_brain_observatory_visual_sequences": ["IMSEQ"],
        "allen_brain_observatory_visual_multi_sequences": ["IMSEQ2"],
        "dvd_waitscreen": ["DVD", "HDDVD"],
    }

    session_names = []
    for recording_path in raw_recording_paths:
        end_of_name = str(recording_path).split("_")[-1]
        for our_label, exp_label in session_naming_dict.items():
            if end_of_name in exp_label:
                session_names.append(our_label)
        else:
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


def chronologize_paths(recording_paths: list[str]):
    """
    For a given set of paths, put them in chronological order
    """
    # get basenames of the recordings
    basenames = [os.path.basename(s) for s in recording_paths]
    # split the basename by the first "-" and take only the latter split
    time_dates = [s.split("-", 1)[-1] for s in basenames]
    # reorganise recording_paths based on np.argsort(time_dates)
    recording_paths_array = np.array(recording_paths)[np.argsort(time_dates)]
    return recording_paths_array.tolist()
