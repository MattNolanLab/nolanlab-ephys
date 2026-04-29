"""
Tools to compute and plot information related to the quality of your recording. 
These are specifically designed for NeuroPixels probes.
"""

import matplotlib.pyplot as plt
import numpy as np
from spikeinterface.core import get_noise_levels
from spikeinterface.widgets import plot_motion, plot_drift_raster_map
from spikeinterface.curation import bombcell_label_units

def compute_noise_across_time(preprocessed_recording):
    """
    Computes the noise on each channel, for each minute of the recording.
    A good quality recording should have a stable noise profile over time.
    """

    channel_noise_per_minute = []   
    minutes_in_recording = int(np.floor(preprocessed_recording.get_duration()/60))
    for minute in range(minutes_in_recording):
        one_minute_recording = preprocessed_recording.frame_slice(start_frame=30_000*60*minute, end_frame = 30_000*60*(minute+1))
        noise = get_noise_levels(one_minute_recording, method='rms')
        channel_noise_per_minute.append(noise)

    return channel_noise_per_minute

def plot_noise_across_time(channel_noise_per_minute, output_filename):
    """
    Plots the output from `compute_noise_across_time`
    """

    fig, ax = plt.subplots(figsize=(6,3))
    
    im = ax.imshow(np.log(np.transpose(channel_noise_per_minute)), aspect='auto', cmap='terrain')
    
    ax.set_xlabel('time (min)')
    ax.set_ylabel('channel (depth sorted)')
    ax.set_title('Log RMS noise across time')

    fig.colorbar(im)

    fig.tight_layout()
    fig.savefig(output_filename)

    return fig

def plot_motion_vector(motion, output_filename):
    """
    Plots motion vector (estimated motion of probe over time), computed in `spikeinterface.compute_motion`
    """

    fig = plot_motion(motion)
    fig.figure.savefig(output_filename)

    return fig


def plot_drift_map(motion_info, output_filename):
    """
    Plots drift map (detected spikes over time), computed in `spikeinterface.compute_motion`
    """

    fig = plot_drift_raster_map(
        peaks = motion_info['peaks'], 
        peak_locations=motion_info['peak_locations'], 
        sampling_frequency=30_000
    )

    fig.figure.savefig(output_filename)

    return fig

def compute_noise_and_good_units(analyzer):
    """
    Computes depth-related quantities.
      - The depth of "good" and "mua" units
      - The noise profile as a function of depth
    """

    distance_between_shanks = 250

    unit_locations = analyzer.get_extension('unit_locations').get_data()
    bombcell_labels = bombcell_label_units(analyzer)['bombcell_label'].values

    shank_ids = analyzer.get_probe().shank_ids
    unique_shanks = np.unique(shank_ids)

    good_units_per_shank = {'0': [], '1': [], '2': [], '3':[]}
    mua_units_per_shank = {'0': [], '1': [], '2': [], '3':[]}

    for bombcell_label, unit_location in zip(bombcell_labels, unit_locations):
        closest_shank = np.argmin(np.array([abs(unit_location[0] - distance_between_shanks*a) for a in range(4)]))
        if bombcell_label == 'good':
            good_units_per_shank[str(closest_shank)].append(unit_location[1])
        elif bombcell_label == 'mua':
            mua_units_per_shank[str(closest_shank)].append(unit_location[1])

    y_locations_per_shank = {'0': [], '1': [], '2': [], '3':[]}
    noise_per_shank = {'0': [], '1': [], '2': [], '3':[]}
    noise_levels = analyzer.get_extension('noise_levels').get_data()
    for shank_id, channel_location, noise_level in zip(analyzer.get_probe().shank_ids, analyzer.get_channel_locations(), noise_levels):
        if (channel_location[0] % distance_between_shanks) == 0:
            y_locations_per_shank[shank_id].append(channel_location[1])
            noise_per_shank[shank_id].append(noise_level)

    return unique_shanks, noise_per_shank, y_locations_per_shank, mua_units_per_shank, good_units_per_shank

def plot_noise_and_good_units(unique_shanks, noise_per_shank, y_locations_per_shank, mua_units_per_shank, good_units_per_shank, output_filename):
    """
    Plots the output from `compute_noise_and_good_units`.
    """

    number_of_shanks = len(unique_shanks)
    fig, axes = plt.subplots(1,2*number_of_shanks, figsize=(4*number_of_shanks, 4))

    for shank_index, shank_id in enumerate(unique_shanks):

        plot_index = 2*shank_index

        noise_on_shank = noise_per_shank[shank_id]
        noise_low, noise_high = np.percentile(noise_on_shank, [0,98])
        axes[plot_index].scatter(noise_on_shank, y_locations_per_shank[shank_id])

        axes[plot_index].set_title(f'Noise vs Depth\nShank {shank_id}', size=8)
        axes[plot_index].set_xlim(noise_low, noise_high)
        axes[plot_index].set_ylabel('Depth (um)')

        ylims = axes[plot_index].get_ylim()

        plot_index += 1

        axes[plot_index].scatter([0]*len(mua_units_per_shank[shank_id]), mua_units_per_shank[shank_id] , color='orange')
        axes[plot_index].scatter([0]*len(good_units_per_shank[shank_id]), good_units_per_shank[shank_id] , color='green')

        axes[plot_index].set_yticklabels([])
        axes[plot_index].set_title('Good (green) and \nmua (orange) units', size=8)
        axes[plot_index].set_ylim(ylims[0], ylims[1])

    fig.savefig(output_filename)