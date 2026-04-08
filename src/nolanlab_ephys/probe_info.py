import numpy as np
import matplotlib.pyplot as plt

import spikeinterface.full as si

"""
Function to make a simple plot of a Neuropixels 2.0 probe, showing (approx) which channels were active during the recording.

In the following, a probe looks like this:

1A 1B 1C 1D
2A 2B 2C 2D
3A 3B 3C 3D
4A 4B 4C 4D 
"""

dx = 250.0
dy = 720.0

locs_to_blocks = {
    "1A": [dx * 0, dy * 3],
    "1B": [dx * 1, dy * 3],
    "1C": [dx * 2, dy * 3],
    "1D": [dx * 3, dy * 3],
    "2A": [dx * 0, dy * 2],
    "2B": [dx * 1, dy * 2],
    "2C": [dx * 2, dy * 2],
    "2D": [dx * 3, dy * 2],
    "3A": [dx * 0, dy * 1],
    "3B": [dx * 1, dy * 1],
    "3C": [dx * 2, dy * 1],
    "3D": [dx * 3, dy * 1],
    "4A": [dx * 0, dy * 0],
    "4B": [dx * 1, dy * 0],
    "4C": [dx * 2, dy * 0],
    "4D": [dx * 3, dy * 0],
}


def rec_to_simple_probe(rec_path):
    """For a given recording, give a simple 16-element representation of a probe. Useful for quick plots."""

    rec = si.read_openephys(rec_path)
    channel_locations = rec.get_channel_locations()

    data_row = [
        np.any(np.all(np.array(loc) == list(channel_locations), axis=1))
        for loc in locs_to_blocks.values()
    ]

    return data_row


def make_probe_plot(rec_path, save_path):

    try:
        probe_vector_representation = rec_to_simple_probe(rec_path)

        matrix_representation = np.reshape(probe_vector_representation, (4, 4))

        fig, ax = plt.subplots()
        ax.imshow(matrix_representation.astype("float"))
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(save_path)

    except:
        print("Could not make probe plot.")

    return
