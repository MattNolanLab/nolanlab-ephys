from argparse import ArgumentParser
from pathlib import Path
import spikeinterface.full as si
from nolanlab_ephys.utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.sort import do_sorting_pipeline_concat_then_split


def main():

    parser = ArgumentParser()

    parser.add_argument('mouse')
    parser.add_argument('date')
    parser.add_argument('protocol')
    parser.add_argument('--data_folder', default=None)
    parser.add_argument('--deriv_folder', default=None)

    mouse = parser.parse_args().mouse
    date = parser.parse_args().date
    protocol = parser.parse_args().protocol

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = "/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Bri/optetrode_recordings/chR2/"
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = "/home/nolanlab/Work/Bri_Project/derivatives/chR2"
    deriv_folder = Path(deriv_folder)

    mouseday_deriv_folder = deriv_folder / f"{mouse}/{date}"
    mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)

    recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=date)
    )
    print(f"\nWill sort the following recordings:")
    for recording_path in recording_paths:
        print(f"  - {recording_path}")

    sessions = [recording_path.name.split('_')[-1] for recording_path in recording_paths]

    analyzer_paths = [mouseday_deriv_folder / f"{session}/{protocol}/sub-{mouse}_date-{date}_ses-{session}_srt-{protocol}_analyzer" for session in sessions]

    print(f"\nAnd save them here:")
    for analyzer_path in analyzer_paths:
        print(f"  - {analyzer_path}")

    recordings = [si.read_openephys(recording_path, stream_id = "CH") for recording_path in recording_paths]

    do_sorting_pipeline_concat_then_split(
        recordings,
        analyzer_paths,
        protocol,
        sorting_output_folder=f"sorting_output_{mouse}_{date}_{protocol}",
        n_jobs=8,
    )


if __name__ == "__main__":
    main()