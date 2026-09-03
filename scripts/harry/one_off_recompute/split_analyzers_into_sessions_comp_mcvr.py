import subprocess

import spikeinterface.full as si

import pandas as pd
from nolanlab_ephys.sort import generic_postprocessing
from pathlib import Path
from argparse import ArgumentParser


data_folder = Path("/exports/eddie/scratch/chalcrow/harry/data/")
deriv_folder = Path("/exports/eddie/scratch/chalcrow/harry/derivatives/")

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)

all_rec_samples = pd.read_csv("scripts/harry/resources/all_rec_samples_involving_mcvr.csv")
samples = all_rec_samples.query(f'mouse == {mouse} & date == {day}')

one_name, one_samples, two_name, two_samples = samples[['one_name', 'one_samples', 'two_name', 'two_samples']].values[0]

print(one_samples, two_samples)

si.set_global_job_kwargs(n_jobs=8)

analyzer_path = deriv_folder / f"M{mouse}/D{day}/full/kilosort4/sub-{mouse}_ses-{day}_srt-kilosort4_full_analyzer.zarr"
analyzer = si.load_sorting_analyzer(analyzer_path)

sorting = analyzer.sorting
recording = analyzer.recording

of1_sorting = sorting.frame_slice(start_frame=0, end_frame=one_samples)
of1_recording = recording.frame_slice(start_frame=0, end_frame=one_samples)

vr_sorting = sorting.frame_slice(start_frame=one_samples, end_frame=None)
vr_recording = recording.frame_slice(start_frame=one_samples, end_frame=None)

sortings = [of1_sorting, vr_sorting]
recordings = [of1_recording, vr_recording]
typs = [one_name, two_name]

for recording, sorting, typ in zip(recordings, sortings, typs):

    # we do all our syncing assuming that t=0 is at the start of the ephys data
    recording._recording_segments[0].t_start = 0

    analyzer_folder = deriv_folder / f"M{mouse:02d}/D{day:02d}/{typ.lower()}/kilosort4/sub-M{mouse:02d}_ses-D{day:02d}_typ-{typ}_srt-kilosort4_analyzer"

    analyzer = si.create_sorting_analyzer(
        recording=recording,
        sorting=sorting, 
        folder = analyzer_folder,
        format = "zarr",
        peak_sign = "both",
        radius_um = 70,
        overwrite=True,
    )

    analyzer.compute(generic_postprocessing)

    subprocess.run(["rm", "-r", str(Path(str(analyzer_folder) + '.zarr') / "extensions/waveforms")]) 


