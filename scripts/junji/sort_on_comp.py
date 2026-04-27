from argparse import ArgumentParser
from loadi.loaders.junji import JunjiSession
from pathlib import Path
import spikeinterface.full as si
import numpy as np
import shutil

def main():

    parser = ArgumentParser()

    parser.add_argument('mouse')
    parser.add_argument('day')
    parser.add_argument('sessions')
    parser.add_argument('protocol')
    parser.add_argument('--data_folder', default=None)
    parser.add_argument('--deriv_folder', default=None)

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = "/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/Junji/Data/"
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = "/home/nolanlab/Work/Yiming_Project/Junji/derivatives"
    deriv_folder = Path(deriv_folder)

    sessions_string = parser.parse_args().sessions
    session_names = sessions_string.split(',')

    mouse = int(parser.parse_args().mouse)
    day = int(parser.parse_args().day)

    protocol = parser.parse_args().protocol

    do_sorting(mouse, day, session_names, protocol, data_folder, deriv_folder)


def do_sorting(mouse, day, session_names, protocol, data_folder, deriv_folder):

    junji_sessions = [JunjiSession(mouse, day, session_name, data_folder) for session_name in session_names]

    recs = [session.get_ephys() for session in junji_sessions]

    split_rec = si.concatenate_recordings(recs).split_by('group')
    removed_channels_recs = si.detect_and_remove_bad_channels(split_rec, method='std', std_mad_threshold=1.2, seed=1205)

    good_channel_ids = np.array([])
    for removed_channels_rec in removed_channels_recs.values():
        good_channel_ids = np.concat([good_channel_ids, removed_channels_rec.channel_ids])

    sorting = si.run_sorter("mountainsort5", removed_channels_recs, verbose=True, remove_existing_folder=True, detect_threshold = 5.0, folder=f"M{mouse}_D{day}_mountainsort_ouput")

    cumulative_samples = 0
    for rec, session_name in zip(recs, session_names):

        mouseday_deriv_folder = deriv_folder / f"M{mouse:02d}/D{day:02d}/{session_name}/{protocol}"
        mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)

        # we do all our syncing assuming that t=0 is at the start of the ephys data
        rec = rec.select_channels(good_channel_ids)
        rec._recording_segments[0].t_start = 0

        recording_total_samples = rec.get_total_samples()
        one_sorting = {sort_id: sort.frame_slice(cumulative_samples, cumulative_samples+recording_total_samples) for sort_id, sort in sorting.items()}
        cumulative_samples += recording_total_samples

        analyzer = si.create_sorting_analyzer(
            recording=si.bandpass_filter(rec.split_by('group')), 
            sorting=one_sorting, 
            folder = mouseday_deriv_folder / f"sub-{mouse:02d}_day-{day:02d}_ses-{session_name}_srt-{protocol}_analyzer",
            format = "binary_folder",
            peak_sign = "both",
            radius_um = 70,
        )

        analyzer.compute({
            'noise_levels': {},
            'unit_locations': {},
            'random_spikes': {},
            'templates': {},
            'isi_histograms': {},
            'waveforms': {},
            'principal_components': {},
            'amplitude_scalings': {},
            'spike_amplitudes': {},
            'spike_locations': {},
            'correlograms': {},
            'template_similarity': {'method': 'l2'},
            'quality_metrics': {'metric_names': ['num_spikes', 'firing_rate', 'presence_ratio', 'snr', 'isi_violation', 'rp_violation', 'sliding_rp_violation', 'synchrony', 'firing_range', 'amplitude_cv', 'amplitude_cutoff', 'noise_cutoff', 'amplitude_median', 'drift', 'sd_ratio', 'mahalanobis', 'd_prime', 'nearest_neighbor', 'silhouette', 'nn_advanced']},
            'template_metrics': {'include_multi_channel_metrics': False},
        })

if __name__ == "__main__":
    main()