import spikeinterface.full as si
from pathlib import Path
from nolanlab_ephys.si_protocols import protocols
from argparse import ArgumentParser
from nolanlab_ephys.si_protocols import generic_postprocessing

activate_projects_path = Path("/run/user/1000/gvfs/smb-share:server=cmvm.datastore.ed.ac.uk,share=cmvm/sbms/groups/CDBS_SIDB_storage/NolanLab/ActiveProjects/")

parser = ArgumentParser()
parser.add_argument('filepaths')
filepaths_string = parser.parse_args().filepaths
recording_paths = filepaths_string.split(',')

protocol = "herdingspikesA"
protocol_info = protocols[protocol]

recording = si.concatenate_recordings([si.read_openephys(activate_projects_path / recording_path) for recording_path in recording_paths])

pp_recording = si.apply_preprocessing_pipeline(recording, protocol_info['preprocessing'])

sorting = si.run_sorter(recording=recording, **protocol_info['sorting'], remove_existing_folder=True)

analyzer = si.create_sorting_analyzer(
    recording=si.apply_preprocessing_pipeline(recording, protocol_info['preprocessing_for_analyzer']), 
    sorting=sorting, 
    folder = "my_analyzer",
    format = "binary_folder"
)

analyzer.compute(generic_postprocessing)
