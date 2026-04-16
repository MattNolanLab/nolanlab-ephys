"""
This script is the pipeline step:

|-----------|            |------------------|
| raw ephys |    --->    | sorting analyzer |
|-----------|            |------------------|

It can be called from the command line. An example:

uv run sort_on_comp.py --mouse 6 --day 12 --sessions OF1,VR,OF2 --protocols kilosort4A --data_folder /home/nolanlab/Work/Harry_Project/data/ --deriv_folder /home/nolanlab/Work/Harry_Project/derivatives/

This will take the ephys data for mouse "6" on day "12" for the three session types "OF1", "VR" and "OF2",
and sort them using protocol "kilosort4A", as described in `nolanlab-ephys/src/nolanlab_ephy/si_protocols.py`.
We sort all three sessions together as one, but produce a sorting analyzer for each one.

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
                {protocol}/
                    sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer
                    sub-06_day-12_ses-OF1_srt-kilosort4A_analyzer.zarr    <---- example
"""

from argparse import ArgumentParser
from nolanlab_ephys.sort import do_sorting_pipeline_concat
from nolanlab_ephys.common_paths import (
    eddie_chris_data_folder,
    eddie_chris_deriv_folder,
)

def main():

    # Parse the user input

    parser = ArgumentParser()
    parser.add_argument("protocol")
    protocol = parser.parse_args().protocol

    recording_paths = [eddie_chris_data_folder / 'sub-UCLA034_ses-3537d970-f515-4786-853f-23de525e110f_desc-raw_ecephys.nwb']
    analyzer_paths = [ eddie_chris_deriv_folder / f"IBL_{protocol}_analyzer" ]

    do_sorting_pipeline_concat(
        recording_paths,
        analyzer_paths,
        protocol,
        n_jobs=8,
    )

if __name__ == "__main__":
    main()

