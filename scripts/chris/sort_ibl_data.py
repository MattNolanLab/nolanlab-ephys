"""
Sorts the IBL data from
    https://dandiarchive.org/dandiset/000409/0.260309.1324/files?location=sub-UCLA034&page=1
For a variety of sorting protocols.
"""

import random
from pathlib import Path
from argparse import ArgumentParser

import spikeinterface.full as si

from nolanlab_ephys.sort import do_sorting_pipeline_concat


def main():

    parser = ArgumentParser()
    parser.add_argument('protocol')
    protocol = parser.parse_args().protocol

    num = random.randint(0, 1000)

    deriv_folder = Path("/exports/eddie/scratch/chalcrow/chris/derivatives")

    recording_path = "/exports/eddie/scratch/chalcrow/chris/raw/sub-UCLA034_ses-3537d970-f515-4786-853f-23de525e110f_desc-raw_ecephys.nwb"
    recordings = [si.read_nwb_recording(recording_path, electrical_series_path='acquisition/ElectricalSeriesProbe00AP')]

    analyzer_path = deriv_folder / f"ibl_{protocol}_analyzer_{num}"

    analyzer = do_sorting_pipeline_concat(
        recordings,
        analyzer_path,
        protocol,
        sorting_output_folder=f"sorting_output_{protocol}_{num}",
        n_jobs=8,
    )

    analyzer.compute(['principal_components', 'quality_metrics'])


if __name__ == "__main__":
    main()
