import spikeinterface.full as si

from nolanlab_ephys.si_protocols import protocols
from nolanlab_ephys.utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.si_protocols import generic_postprocessing

def do_sorting_pipeline_concat_then_split(mouse, day, sessions, data_folder, deriv_folder, protocol):
    """
    Concatenates all recordings into one and sorts, then splits the large sorting into a sorting per session.
    """

    protocol_info = protocols[protocol]

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day)
    )
    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]
    concatenated_recording = si.concatenate_recordings(recordings)

    pp_recording = si.apply_preprocessing_pipeline(
        concatenated_recording, protocol_info["preprocessing"]
    )
    sorting = si.run_sorter(
        recording=pp_recording,
        **protocol_info["sorting"],
        remove_existing_folder=True,
        verbose=True,
        folder=f"M{mouse}_D{day}_{protocol}_{'-'.join(sessions)}_output",
    )

    cumulative_samples = 0
    for recording, session in zip(recordings, sessions, strict=True):

        # we do all our syncing assuming that t=0 is at the start of the ephys data, for each session
        recording.segments[0].t_start = 0

        # We have one big sorting from our concatenated recordings. Split this into individual sessions:
        recording_total_samples = recording.get_total_samples()
        one_sorting = sorting.frame_slice(
            cumulative_samples, cumulative_samples + recording_total_samples
        )
        cumulative_samples += recording_total_samples

        analyzer_path = (
            deriv_folder
            / f"M{mouse:02d}/D{day:02d}/{session}/{protocol}/sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer",
        )
        analyzer = si.create_sorting_analyzer(
            recording=si.apply_preprocessing_pipeline(
                recording, protocol_info["preprocessing_for_analyzer"]
            ),
            sorting=one_sorting,
            folder=analyzer_path,
            format="zarr",
            peak_sign="both",
            radius_um=70,
        )

        analyzer.compute(generic_postprocessing)

    return


def do_sorting_pipeline_concat(mouse, day, sessions, data_folder, deriv_folder, protocol):
    """
    Concatenates all recordings into one and sorts, and makes an analyzer.
    Note that all, e.g., quality metrics are computed for concatenated recordings, rather than each session.
    """

    protocol_info = protocols[protocol]

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day)
    )
    recordings = [si.read_openephys(recording_path) for recording_path in recording_paths]
    concatenated_recording = si.concatenate_recordings(recordings)

    pp_recording = si.apply_preprocessing_pipeline(
        concatenated_recording, protocol_info["preprocessing"]
    )
    sorting = si.run_sorter(
        recording=pp_recording,
        **protocol_info["sorting"],
        remove_existing_folder=True,
        verbose=True,
        folder=f"M{mouse}_D{day}_{protocol}_{'-'.join(sessions)}_output",
    )

    analyzer_path = (
        deriv_folder
        / f"M{mouse:02d}/D{day:02d}/full/{protocol}/sub-{mouse:02d}_day-{day:02d}_srt-{protocol}_analyzer",
    )
    analyzer = si.create_sorting_analyzer(
        recording=si.apply_preprocessing_pipeline(
            concatenated_recording, protocol_info["preprocessing_for_analyzer"]
        ),
        sorting=sorting,
        folder=analyzer_path,
        format="zarr",
        peak_sign="both",
        radius_um=70,
    )

    analyzer.compute(generic_postprocessing)

    return