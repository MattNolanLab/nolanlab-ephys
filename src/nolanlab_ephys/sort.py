from datetime import datetime

import spikeinterface.full as si

from nolanlab_ephys.spikeinterface_tools import protocols
from nolanlab_ephys.spikeinterface_tools import generic_postprocessing


def do_sorting_pipeline_concat_then_split(
    recordings,
    analyzer_paths,
    protocol: str,
    sorting_output_folder=None,
    n_jobs=1,
):
    """
    Concatenates all recordings into one and sorts them.
    Then splits the large sorting into a sorting per session, and creates and analyzer for each.
    """

    if len(recordings) != len(analyzer_paths):
        raise ValueError("length of `recording_paths` not equal to length of `analyzer_paths`")

    si.set_global_job_kwargs(n_jobs=n_jobs)

    if sorting_output_folder is None:
        sorting_output_folder = (
            f"sorting_output_{protocol}_{datetime.now().strftime(format='%d-%m-%Y_%H-%M-%S')}"
        )

    protocol_info = protocols[protocol]

    concatenated_recording = si.concatenate_recordings(recordings)

    pp_recording = si.apply_preprocessing_pipeline(
        concatenated_recording, protocol_info["preprocessing"]
    )
    sorting = si.run_sorter(
        recording=pp_recording,
        **protocol_info["sorting"],
        remove_existing_folder=True,
        verbose=True,
        folder=sorting_output_folder,
    )

    cumulative_samples = 0
    for recording, analyzer_path in zip(recordings, analyzer_paths, strict=True):
        # we do all our syncing assuming that t=0 is at the start of the ephys data, for each session
        recording.segments[0].t_start = 0

        # We have one big sorting from our concatenated recordings. Split this into individual sessions:
        recording_total_samples = recording.get_total_samples()
        one_sorting = sorting.frame_slice(
            cumulative_samples, cumulative_samples + recording_total_samples
        )
        cumulative_samples += recording_total_samples

        preprocessed_recording_for_analyzer = si.apply_preprocessing_pipeline(
            recording, protocol_info["preprocessing_for_analyzer"]
        )

        analyzer = si.create_sorting_analyzer(
            recording=preprocessed_recording_for_analyzer,
            sorting=one_sorting,
            folder=analyzer_path,
            format="zarr",
            peak_sign="both",
            radius_um=70,
        )

        analyzer.compute(generic_postprocessing)

    return


def do_sorting_pipeline_concat(
    recordings,
    analyzer_path,
    protocol: str,
    sorting_output_folder=None,
    n_jobs=1,
):
    """
    Concatenates all recordings into one and sort them, then creates an analyzer for concatenated recording.
    Note that all, e.g., quality metrics are computed for concatenated recordings, rather than each session.
    """

    if sorting_output_folder is None:
        sorting_output_folder = (
            f"sorting_output_{protocol}_{datetime.now().strftime(format='%d-%m-%Y_%H-%M-%S')}"
        )

    protocol_info = protocols[protocol]

    si.set_global_job_kwargs(n_jobs=n_jobs)

    concatenated_recording = si.concatenate_recordings(recordings)

    pp_recording = si.apply_preprocessing_pipeline(
        concatenated_recording, protocol_info["preprocessing"]
    )
    sorting = si.run_sorter(
        recording=pp_recording,
        **protocol_info["sorting"],
        remove_existing_folder=True,
        verbose=True,
        folder=sorting_output_folder,
    )

    # we do all our syncing assuming that t=0 is at the start of the ephys data
    concatenated_recording.segments[0].t_start = 0

    preprocessed_recording_for_analyzer = si.apply_preprocessing_pipeline(
        concatenated_recording, protocol_info["preprocessing_for_analyzer"]
    )

    analyzer = si.create_sorting_analyzer(
        recording=preprocessed_recording_for_analyzer,
        sorting=sorting,
        folder=analyzer_path,
        format="zarr",
        peak_sign="both",
        radius_um=70,
    )

    analyzer.compute(generic_postprocessing)

    return
