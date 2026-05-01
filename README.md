# Nolanlab Ephys

This is the main repo for processing ephys data in the Nolan Lab. The pipeline step takes in raw ephys data and outputs a [SpikeInterface](https://github.com/SpikeInterface/spikeinterface) [sorting analyzer](https://spikeinterface.readthedocs.io/en/stable/modules/postprocessing.html):

 ![An ephys analysis pipeline](ephys_pipeline.png)

It will take in raw ephys recordings

```
data_folder/
    global_session_type/
        M{mouse:02d}_D{day:02d}_*_{session_type}/
            Record Node 109/         <---- (or whatever openephys spits out)
```

And output `SortingAnalyzer`s and quality control plots with the naming convention:

```
deriv_folder/
    M{mouse:02d}/
        D{day:02d}/
            probe_layout.pdf
            {session_type}/
                {protocol}/
                    sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer
                    recording_quality_plots/
                        sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_noise_across_time.png
                        etc.
```

Read about the entire NolanLab pipeline: https://github.com/MattNolanLab/analysis_pipelines

## Code organisation

We use a source/scripts workflow. Source code (in the `src/nolanlab-ephys` folder) is meant to be fairly stable. Think hard before you modify it: it's designed to work with all the experiments in the lab. Scripts (in `scripts/{experimenters_name}`) are for bespoke, custom, individual code. You can make many scripts to do many things, or try out new ideas. 

This repo represents a _minimum viable product_: it contains a working spike sorting pipeline. But it has been forked and modified when applied to other projects in the lab. The code based on this repo used for individual experiments in the lab can be found here:

- [Harry](https://chrishalcrow.github.io/harry_data_readme/): https://github.com/chrishalcrow/nolanlab-ephys/tree/main/scripts/harry
- [Wolf](https://chrishalcrow.github.io/wolf_data_readme/): https://github.com/chrishalcrow/nolanlab-ephys/tree/main/scripts/wolf
- Bri : https://github.com/chrishalcrow/nolanlab-ephys/tree/main/scripts/bri
- Teris: https://github.com/chrishalcrow/nolanlab-ephys/tree/main/scripts/teris
- Junji: https://github.com/chrishalcrow/nolanlab-ephys/tree/main/scripts/junji
- Sorting IBL data from DANDI: https://github.com/chrishalcrow/nolanlab-ephys/blob/main/scripts/chris/sort_ibl_data.py

Note that the modifications are contained to the scripts folder. The source folder is identical to the source folder here.

## Use on your own computer

First step: get something working on your computer using either your own data or someone else's that is on the DataStore. You could even try it on some openly available data from DANDI. E.g. the code in [this fork](https://github.com/chrishalcrow/nolanlab-ephys/blob/main/scripts/chris/sort_ibl_data.py) sorts [this data](https://dandiarchive.org/dandiset/000409/0.260309.1324/files?location=sub-UCLA034&page=1).

We recommend that you make a fork (your own personal copy) of this repo by clicking `Fork -> Create new fork` above. To begin using the fork on your computer, please download (clone) the repo from github. Then enter the directory and start using the codebase!

```
git clone https://github.com/your_GitHub_username/nolanlab-ephys
cd nolanlab-ephys
```

You can immediately run code using [`uv`](https://docs.astral.sh/uv/getting-started/installation/). The most important script is `sort_on_comp.py`, which does the actual spike sorting. To run this script, do this:

```
uv run scripts/template/sort_on_comp.py 25 25 VR kilosort4 --data_folder /path/to/data/folder --deriv_folder /path/to/deriv/folder
```

Read more about the `sort_on_comp.py` script by opening the file: there's lots of documentation inside.

The different spike sorting protocols can be found in `src/nolanlab_ephys/spikeinterface_tools.py`.

You can visualise the results using e.g.

```
uv run scripts/template/visualise_results.py 25 25 VR kilosort4 --deriv_folder /path/to/deriv/folder
```

## Using on EDDIE

The package is designed to be used on the Nolan Lab's data on your local computer or on EDDIE, the Edinburgh supercomputer. There is more extensive information about using EDDIE here: https://chrishalcrow.github.io/uv_on_eddie/

In brief, to run a spike sorting pipeline on Eddie, do the following. First, log on to EDDIE and get a login node:

``` bash
ssh edinburgh_username@eddie.ecdf.ed.ac.uk
... wait to get on to eddie ...
qlogin -l h_vmem=8G
```

We'll now install this package. EDDIE has a 2TB scratch you can use to put stuff in. We'll navigate to there (then into wherever you want to store this code. I've made a `my_project/code` folder), download ("clone") this package, then navigate into the package:

``` bash
cd /exports/eddie/scratch/chalcrow/my_project/code
git clone https://github.com/MattNolanLab/nolanlab-ephys.git
cd nolanlab-ephys
```

Now you can run some scripts! Here's an example on my login (note: you need to change chalcrow to something else):

``` bash
uv run scripts/template/sort_on_eddie.py 25 25 OF1,VR,OF2 kilosort4A --data_folder /exports/eddie/scratch/chalcrow/harry/data/ --deriv_folder /exports/eddie/scratch/chalcrow/harry/derivatives
```
