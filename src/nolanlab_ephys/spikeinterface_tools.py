from pathlib import Path

import spikeinterface.full as si
from spikeinterface.curation.curation_tools import resolve_merging_graph
from spikeinterface.curation import validate_curation_dict


"""
Protocols we use for spike sorting. Each protocol has a unique name of the form {sorter_name}{letter}. The protocol consists of three stages

  1. The preprocessing steps applied before sorting.
  2. The kwargs passed to `run_sorter` from SpikeInterface.
  3. The preprocessing steps applied to the recording before constructing the analyzer.

Understanding the details of these require understanding SpikeInterface. Here's a good place to start: https://spikeinterface.readthedocs.io/en/stable/get_started/quickstart.html
"""
protocols = {
    "kilosort4A": {
        "preprocessing": {
            "detect_and_remove_bad_channels": {"seed": 1205},
            "phase_shift": {},
        },
        "sorting": {
            "sorter_name": "kilosort4",
            "do_correction": False,
            "use_binary_file": False,
        },
        "preprocessing_for_analyzer": {
            "detect_and_remove_bad_channels": {"seed": 1205},
            "phase_shift": {},
            "common_reference": {},
            "bandpass_filter": {},
        },
    },
    'kilosort4B': {
        'preprocessing': {
            'phase_shift': {},
        },
        'sorting': {
            'sorter_name': 'kilosort4',
            'do_correction': True,
            'use_binary_file': False,
        },
        'preprocessing_for_analyzer': {
            'phase_shift': {},
            'common_reference': {},
            'bandpass_filter': {},
        },
    },
    "mountainsort5A": {
        "preprocessing": {},
        "sorting": {
            "sorter_name": "mountainsort5",
            "scheme": "2",
        },
        "preprocessing_for_analyzer": {
            "common_reference": {},
            "bandpass_filter": {},
        },
    },
    "mountainsort5B": {
        "preprocessing": {},
        "sorting": {
            "sorter_name": "mountainsort5",
            "scheme": "3",
        },
        "preprocessing_for_analyzer": {
            "common_reference": {},
            "bandpass_filter": {},
        },
    },
    "mountainsort4A": {
        "preprocessing": {},
        "sorting": {
            "sorter_name": "mountainsort4",
        },
        "preprocessing_for_analyzer": {
            "common_reference": {},
            "bandpass_filter": {},
        },
    },
    "herdingspikesA": {
        "preprocessing": {
            "bandpass_filter": {},
            "common_reference": {},
        },
        "sorting": {
            "sorter_name": "herdingspikes",
        },
        "preprocessing_for_analyzer": {
            "bandpass_filter": {},
            "common_reference": {},
        },
    },
    "spykingcircus2A": {
        "preprocessing": {},
        "sorting": {
            "sorter_name": "spykingcircus2",
            "apply_motion_correction": False,
            "cache_preprocessing": {"mode": "folder", "folder": "sk2_pre"},
        },
        "preprocessing_for_analyzer": {
            "bandpass_filter": {},
            "common_reference": {},
        },
    },
    'spykingcircus2B': {
        'preprocessing': {
        },
        'sorting': {
            'sorter_name': 'spykingcircus2',
            'apply_motion_correction': True,
            "cache_preprocessing": {
                "mode": "folder",
                "folder": "sk2_pre"
            },
        },
        'preprocessing_for_analyzer': {
            'bandpass_filter': {},
            'common_reference': {},
        },
    },
    "tridesclous2A": {
        "preprocessing": {},
        "sorting": {
            "sorter_name": "tridesclous2",
            "cache_preprocessing_mode": "folder",
        },
        "preprocessing_for_analyzer": {
            "bandpass_filter": {},
            "common_reference": {},
        },
    },
    'tridesclous2B': {
        'preprocessing': {
            'apply_motion_correction': True
        },
        'sorting': {
            'sorter_name': 'tridesclous2',
            'cache_preprocessing_mode': 'folder',
        },
        'preprocessing_for_analyzer': {
            'bandpass_filter': {},
            'common_reference': {},
        },
    },

    'lupinA': {
        'preprocessing': {
            'apply_motion_correction': False

        },
        'sorting': {
            'sorter_name': 'tridesclous2',
            'cache_preprocessing_mode': 'folder',
        },
        'preprocessing_for_analyzer': {
            'bandpass_filter': {},
            'common_reference': {},
        },
    },

    'lupinB': {
        'preprocessing': {
            'apply_motion_correction': True,
        },
        'sorting': {
            'sorter_name': 'tridesclous2',
            'cache_preprocessing_mode': 'folder',
        },
        'preprocessing_for_analyzer': {
            'bandpass_filter': {},
            'common_reference': {},
        },
    },
}

generic_postprocessing = {
    "unit_locations": {},
    "random_spikes": {},
    "noise_levels": {},
    "waveforms": {},
    "templates": {},
    "spike_amplitudes": {"peak_sign": "both"},
    "amplitude_scalings": {},
    "isi_histograms": {},
    "spike_locations": {"peak_sign": "both"},
    "correlograms": {},
    "template_similarity": {"method": "l2"},
    "quality_metrics": {},
    "template_metrics": {},
}

def check_protocol_dict(protocol_info):

    for essential_key in ["preprocessing", "sorting", "preprocessing_for_analyzer"]:
        if essential_key not in protocol_info:
            raise ValueError(f"`protocol_info` must contain key '{essential_key}'.")
        else:
            if not isinstance(protocol_info[essential_key], dict):
                raise ValueError(f"protocol_info['{essential_key}'] must be a dict. Currently it is equal to `{protocol_info[essential_key]}`")

    return

def compute_automated_curation(analyzer, model_path, curation_output_path):
    """
    Computes a suggested automated curation of an analyzer, based on a trained model from UnitRefine.
    """

    unitrefine_labels = si.auto_label_units(analyzer, model_folder=model_path, trust_model=True)

    noise_units = list(unitrefine_labels[unitrefine_labels["prediction"] == "noise"].index)

    label_definitions = {
        "quality": dict(name="quality", label_options=["good", "noise"], exclusive=True),
    }

    manual_labels = [
        {
            "unit_id": unit_id,
            "labels": {"quality": [unitrefine_labels.loc[unit_index].values[0]]},
        }
        for unit_index, unit_id in enumerate(analyzer.unit_ids)
    ]

    potential_merges = si.compute_merge_unit_groups(
        analyzer.select_units(list(unitrefine_labels.query('prediction == "good"').index)),
        preset="x_contaminations",
        resolve_graph=False,
    )
    more_potential_merges = si.compute_merge_unit_groups(
        analyzer.select_units(list(unitrefine_labels.query('prediction == "good"').index)),
        preset="temporal_splits",
        resolve_graph=False,
    )

    final_merges = resolve_merging_graph(analyzer.sorting, potential_merges + more_potential_merges)

    curation_dict = dict(
        format_version="2",
        unit_ids=analyzer.unit_ids,
        label_definitions=label_definitions,
        merges=[dict(unit_ids=p) for p in final_merges],
        removed=noise_units,
        manual_labels=manual_labels,
    )

    validate_curation_dict(curation_dict)

    # we can use the CurationModel for more secure serialization
    from spikeinterface.curation.curation_model import CurationModel

    curation = CurationModel(**curation_dict)
    curation_file = Path(curation_output_path)
    _ = curation_file.write_text(curation.model_dump_json(indent=4))
