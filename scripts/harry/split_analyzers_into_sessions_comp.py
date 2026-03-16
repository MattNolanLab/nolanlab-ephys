import subprocess

import spikeinterface.full as si

import pandas as pd
from nolanlab_ephys.si_protocols import generic_postprocessing
from pathlib import Path
from argparse import ArgumentParser

data_folder = Path("/exports/eddie/scratch/chalcrow/harry/data/")
deriv_folder = Path("/exports/eddie/scratch/chalcrow/harry/derivatives/")

parser = ArgumentParser()

parser.add_argument('mouse')
parser.add_argument('day')

mouse = int(parser.parse_args().mouse)
day = int(parser.parse_args().day)

all_rec_samples = pd.read_csv("scripts/harry/resources/all_rec_samples_of_vr_of.csv")
samples = all_rec_samples.query(f'mouse == {mouse} & day == {day}')

of1_samples, vr_samples, of2_samples = samples[['of1','vr','of2']].values[0]

print(of1_samples, vr_samples, of2_samples)

si.set_global_job_kwargs(n_jobs=8)

analyzer_path = deriv_folder / f"M{mouse}/D{day}/full/kilosort4/sub-{mouse}_ses-{day}_srt-kilosort4_full_analyzer.zarr"
analyzer = si.load_sorting_analyzer(analyzer_path)

sorting = analyzer.sorting
recording = analyzer.recording

of1_sorting = sorting.frame_slice(start_frame=0, end_frame=of1_samples)
of1_recording = recording.frame_slice(start_frame=0, end_frame=of1_samples)

vr_sorting = sorting.frame_slice(start_frame=of1_samples, end_frame=of1_samples+vr_samples)
vr_recording = recording.frame_slice(start_frame=of1_samples, end_frame=of1_samples+vr_samples)

of2_sorting = sorting.frame_slice(start_frame=of1_samples+vr_samples, end_frame=None)
of2_recording = recording.frame_slice(start_frame=of1_samples+vr_samples, end_frame=None)

sortings = [of1_sorting, vr_sorting, of2_sorting]
recordings = [of1_recording, vr_recording, of2_recording]
typs = ['OF1', 'VR', 'OF2']

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


