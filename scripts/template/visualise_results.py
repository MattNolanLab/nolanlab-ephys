# /// script
# dependencies = [
#   "spikeinterface-gui",
#   "spikeinterface",
#   "numba",
# ]
# ///

from pathlib import Path
from argparse import ArgumentParser

from spikeinterface_gui import run_mainwindow
import spikeinterface.full as si

parser = ArgumentParser()

parser.add_argument("mouse", type=int)
parser.add_argument("day", type=int)
parser.add_argument("session", type=str)
parser.add_argument("protocol", type=str)
parser.add_argument("--deriv_folder", default="/home/nolanlab/Work/Harry_Project/derivatives/", type=str)

args = parser.parse_args()

mouse = args.mouse
day = args.day
session = args.session
protocol = args.protocol

deriv_folder = Path(args.deriv_folder)

mouseday_path = deriv_folder / f'M{mouse:02d}/D{day:02d}/{session.lower()}/{protocol}'
analyzer_path = mouseday_path / f'sub-M{mouse:02d}_ses-D{day:02d}_typ-{session}_srt-{protocol}_analyzer.zarr'

analyzer = si.load_sorting_analyzer(analyzer_path)

run_mainwindow(
    analyzer,
    mode="desktop",
)
