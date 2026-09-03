import spikeinterface.full as si
import pandas as pd

mouse = 7

M7_folder_names = [
    "M07_TEST_2026-06-06_14-05-13_1",
    "M07_TEST_2026-06-06_14-06-37_2",
    "M07_TEST_2026-06-06_14-07-54_3",
    "M07_TEST_2026-06-06_14-09-13_4",
    "M07_TEST_2026-06-06_14-10-39_5",
    "M07_TEST_2026-06-06_14-11-58_6",
    "M07_TEST_2026-06-06_14-13-17_7",
    "M07_TEST_2026-06-06_14-14-38_8",
    "M07_TEST_2026-06-06_14-16-02_9",
    "M07_TEST_2026-06-06_14-17-29_10",              
    "M07_TEST_2026-06-06_14-18-46_11",
    "M07_TEST_2026-06-06_14-20-08_12",             
    "M07_TEST_2026-06-06_14-21-28_13",
]
M8_folder_names = [
    "M08_TEST_2026-06-06_14-51-03_1",
    "M08_TEST_2026-06-06_14-53-55_2",
    "M08_TEST_2026-06-06_14-55-11_3",
    "M08_TEST_2026-06-06_14-56-26_4",
    "M08_TEST_2026-06-06_14-58-04_5",
    "M08_TEST_2026-06-06_14-59-16_6",
    "M08_TEST_2026-06-06_15-00-29_7",
    "M08_TEST_2026-06-06_15-02-34_8",
    "M08_TEST_2026-06-06_15-04-33_9",
    "M08_TEST_2026-06-06_15-05-44_10",              
    "M08_TEST_2026-06-06_15-07-12_11",             
    "M08_TEST_2026-06-06_15-08-47_12",             
    "M08_TEST_2026-06-06_15-10-02_13",
]
M9_folder_names = [
    "M09_TEST_2026-06-06_15-37-02_1",
    "M09_TEST_2026-06-06_15-38-12_2",
    "M09_TEST_2026-06-06_15-39-22_3",
    "M09_TEST_2026-06-06_15-40-33_4",
    "M09_TEST_2026-06-06_15-41-51_5",
    "M09_TEST_2026-06-06_15-44-07_6",
    "M09_TEST_2026-06-06_15-45-25_7",
    "M09_TEST_2026-06-06_15-46-34_8",
    "M09_TEST_2026-06-06_15-47-44_9",
    "M09_TEST_2026-06-06_15-48-58_10",              
    "M09_TEST_2026-06-06_15-50-07_11",               
    "M09_TEST_2026-06-06_15-51-16_12",
    "M09_TEST_2026-06-06_15-52-26_13",
]
M10_folder_names = [    
    "M10_TEST_2026-06-06_16-28-18_1",
    "M10_TEST_2026-06-06_16-29-27_2",
    "M10_TEST_2026-06-06_16-30-46_3",
    "M10_TEST_2026-06-06_16-31-58_4",
    "M10_TEST_2026-06-06_16-33-12_5",
    "M10_TEST_2026-06-06_16-34-22_6",
    "M10_TEST_2026-06-06_16-35-38_7",
    "M10_TEST_2026-06-06_16-36-54_8",
    "M10_TEST_2026-06-06_16-38-02_9",
    "M10_TEST_2026-06-06_16-39-15_10",
    "M10_TEST_2026-06-06_16-40-36_11",             
    "M10_TEST_2026-06-06_16-42-01_12",
    "M10_TEST_2026-06-06_16-43-31_13",
]

folders_dict = {
    7: M7_folder_names,
    8: M8_folder_names,
    9: M9_folder_names,
    10: M10_folder_names,
}

good_unit_info = pd.DataFrame(columns=['unit_x_loc', 'unit_y_loc'])
mua_unit_info = pd.DataFrame(columns=['unit_x_loc', 'unit_y_loc'])
noise_levels_info = pd.DataFrame(columns=['channel_x_loc', 'channel_y_loc', 'noise_level'])

folder_names = folders_dict[mouse]

for folder_name in folder_names:
    
    analyzer_path = f"/exports/eddie/scratch/chalcrow/derivatvies/{folder_name}_analyzer"
    
    analyzer = si.load_sorting_analyzer(analyzer_path)
    
    bombcell_labels = si.bombcell_label_units(analyzer)['bombcell_label']
    good_units = (bombcell_labels == 'good').values
    mua_units = (bombcell_labels == 'mua').values
    
    unit_locations =  analyzer.get_extension('unit_locations')
    
    unit_locs = unit_locations.get_data()[:,:2]
    good_unit_locs = unit_locs[good_units]
    mua_unit_locs = unit_locs[mua_units]
    
    one_good_unit_info = pd.DataFrame(good_unit_locs, columns=['unit_x_loc', 'unit_y_loc'])
    good_unit_info = pd.concat([good_unit_info, one_good_unit_info])
    
    one_mua_unit_info = pd.DataFrame(mua_unit_locs, columns=['unit_x_loc', 'unit_y_loc'])
    mua_unit_info = pd.concat([mua_unit_info, one_mua_unit_info])
    
    noise_levels = analyzer.get_extension('noise_levels').get_data()
    channel_locations = analyzer.get_channel_locations()
    
    one_noise_levels_info = pd.DataFrame(columns=['channel_x_loc', 'channel_y_loc', 'noise_level'])
    one_noise_levels_info['channel_x_loc'] = channel_locations[:,0]
    one_noise_levels_info['channel_y_loc'] = channel_locations[:,1]
    one_noise_levels_info['noise_level'] = noise_levels
    
    noise_levels_info = pd.concat([noise_levels_info, one_noise_levels_info])

noise_levels_info.to_csv(f'/exports/eddie/scratch/chalcrow/derivatvies/summary/M{mouse}_noise_levels.csv')
good_unit_info.to_csv(f'/exports/eddie/scratch/chalcrow/derivatvies/summary/M{mouse}_good_units.csv')
mua_unit_info.to_csv(f'/exports/eddie/scratch/chalcrow/derivatvies/summary/M{mouse}_mua_units.csv')
