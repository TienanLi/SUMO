import sys
import os
from os import path
import pandas as pd
import numpy as np
from collections import defaultdict
from sumolib import checkBinary
import traci
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


input_volume = 500 #veh/h/lane
LC_rate = 0.2
duration = 600 #s
sim_resolution = .1 #s
np.random.seed(1)


# clear images folder
pic_list = os.listdir('images')
for p in pic_list:
    os.remove(os.path.join('images', p))

# Simulation and data collection
# os.environ['SUMO_HOME'] = '/Users/xi_zhang/sumo/'
os.environ['SUMO_HOME'] = 'C:\\Program Files (x86)\\Eclipse\\Sumo\\'
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


output_path = 'simulation_data_test_' + str(input_volume) + '.csv'
GUI = False
# GUI = True
if GUI:
    traci.start([checkBinary('sumo-gui'), "-c", "test.sumocfg",
                 "--step-length", str(sim_resolution),
                 "--lateral-resolution", "3",
                 "--seed", "1"])
else:
    traci.start([checkBinary('sumo'), "-c", "test.sumocfg",
                 "--step-length", str(sim_resolution),
                 "--lateral-resolution", "3",
                 "--seed", "1"])

data = []
veh_ids = []
curTime = 0
veh_id = 0
vehicle_probability = input_volume / 3600
while duration > curTime:
    if np.random.choice(2, p=[1 - vehicle_probability, vehicle_probability]):
        if np.random.choice(2, p=[1 - LC_rate, LC_rate]):
            arrL = "0"
        else:
            arrL = "1"
        traci.vehicle.add(str(veh_id), "route_0", typeID = "vType_0", departSpeed = "30",
            departLane = "1", arrivalLane = arrL)
        veh_id += 1

    if np.random.choice(2, p=[1 - vehicle_probability, vehicle_probability]):
        if np.random.choice(2, p=[1 - LC_rate, LC_rate]):
            arrL = "1"
        else:
            arrL = "0"
        traci.vehicle.add(str(veh_id), "route_0", typeID = "vType_0", departSpeed = "30",
            departLane = "0", arrivalLane = arrL)
        veh_id += 1

    for i in traci.vehicle.getIDList():
            data.append([i, curTime,
                     traci.vehicle.getLaneID(i),
                     traci.vehicle.getPosition(i),
                     traci.vehicle.getSpeed(i)])

    traci.simulationStep()
    curTime += sim_resolution

    # if 500 * 0.1 <= curTime <= 2000 * 0.1:
    #     curTime += 1
    #     traci.gui.screenshot('View #0', os.getcwd() + "/images/" + str(curTime) + ".png")

print(veh_id)

df = pd.DataFrame(data)
df.to_csv(output_path)

traci.close()
sys.stdout.flush()


# input data
del df
df = pd.read_csv('simulation_data_test_' + str(input_volume) + '.csv', sep=',', header=None)

# Data processing
df = df.drop(index=0)
# col1: veh id; col2: time; col3: lane id; col4: position; col5: speed
posi = df[4].str.replace('(', '')
posi1 = posi.str.replace(')', '')
posi_split = posi1.str.split(', ', expand=True)
# veh_ID = df[1].str.replace('flow_', '')
veh_ID = df[1]
time = pd.to_numeric(df[2])
road_ID = df[3].str.replace('main_', '')
position_x = pd.to_numeric(posi_split[0])
position_y = pd.to_numeric(posi_split[1])
speed = pd.to_numeric(df[5])
raw_data = pd.concat([veh_ID, time, road_ID, position_x, position_y, speed], axis=1, ignore_index=True)
sorted_by_veh_id = raw_data.sort_values(by=[0, 1])


# split info by lane (CF+LC)
lane0_all_data = pd.DataFrame()
lane1_all_data = pd.DataFrame()

lane0_all_data = lane0_all_data.append(sorted_by_veh_id[sorted_by_veh_id[2] == '0'])
lane1_all_data = lane1_all_data.append(sorted_by_veh_id[sorted_by_veh_id[2] == '1'])


# plots
# cf +lc lane0 with speed  color:seismic_r
fig, axs = plt.subplots(1, 1, sharex=True, sharey=True)
for allVeh_0 in pd.unique(lane0_all_data[0]):
    veh_info = lane0_all_data.loc[lane0_all_data[0] == allVeh_0]
    veh_time = veh_info[1]
    veh_position_x = veh_info[3]
    veh_speed = veh_info[5]
    if len(veh_time) <= 1:
        continue
    points = np.array([veh_time, veh_position_x]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0, 30)
    lc = LineCollection(segments, cmap='jet_r', norm=norm)
    lc.set_array(veh_speed)
    lc.set_linewidth(0.5)
    line = axs.add_collection(lc)
fig.colorbar(line, ax=axs)
axs.set_xlim(0, duration*1.1)
axs.set_ylim(100, 1000)
plt.ylabel('Position (m)')
plt.xlabel('Time (s)')
plt.title('Lane 0 trajectory plot - volume: ' + str(input_volume) +'/h/lane')
plt.savefig(str(input_volume) + 'CF_LC_Lane0_position_with_speed', bbox_inches='tight', pad_inches=0.1)
plt.close()


# cf +lc lane1 with speed
fig, axs = plt.subplots(1, 1, sharex=True, sharey=True)
for allVeh_0 in pd.unique(lane1_all_data[0]):
    veh_info = lane1_all_data.loc[lane1_all_data[0] == allVeh_0]
    veh_time = veh_info[1]
    veh_position_x = veh_info[3]
    veh_speed = veh_info[5]
    if len(veh_time) <= 1:
        continue
    points = np.array([veh_time, veh_position_x]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0, 30)
    lc = LineCollection(segments, cmap='jet_r', norm=norm)
    lc.set_array(veh_speed)
    lc.set_linewidth(0.5)
    line = axs.add_collection(lc)
fig.colorbar(line, ax=axs)
axs.set_xlim(0, 200)
axs.set_ylim(100, 1000)
plt.ylabel('Position (m)')
plt.xlabel('Time (s)')
plt.title('Lane 1 trajectory plot - volume: ' + str(input_volume) +'/h/lane')
plt.savefig(str(input_volume) + 'CF_LC_Lane1_position_with_speed', bbox_inches='tight', pad_inches=0.1)
plt.close()


# count veh #
# total_veh_num = len(pd.unique(sorted_by_veh_id[0]))  # 668 in total  # 324 cf 162 in lane0, 162 in lane1
# veh_num_in_cf_all_lane = len(pd.unique(two_lane_cf_data[0]))
# veh_num_in_cf_lane0 = len(pd.unique(lane0_cf_data[0]))
# veh_num_in_cf_lane1 = len(pd.unique(lane1_cf_data[0]))


