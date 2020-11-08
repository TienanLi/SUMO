import sys
import os
import pandas as pd
from collections import defaultdict

os.environ['SUMO_HOME'] = 'C:\\Program Files (x86)\\Eclipse\\Sumo\\'
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary
import traci

output_path = 'simulation_data_test.csv'
GUI = True
sim_resolution = .1
if GUI:
    traci.start([checkBinary('sumo-gui'), "-c", "test.sumocfg",
                 "--step-length", str(sim_resolution),
                 "--default.action-step-length", str(sim_resolution),
                 "--lateral-resolution", "3"])
else:
    traci.start([checkBinary('sumo'),"-c", "test.sumocfg",
                 "--step-length", str(sim_resolution),
                 "--default.action-step-length", str(sim_resolution),
                 "--lateral-resolution", "3"])

data = []

step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    step += 1
    if 100 <= step < 120:
        traci.gui.screenshot("View #0", os.getcwd()+"/images/" + str(step) + ".png")
    traci.simulationStep()
    veh_ids = traci.vehicle.getIDList()
    
    # save to simulation data to file    
    curTime = traci.simulation.getTime()
    for veh_id in veh_ids:
        data.append([veh_id, curTime, 
                     traci.vehicle.getLaneID(veh_id), 
                     traci.vehicle.getPosition(veh_id), 
                     traci.vehicle.getSpeed(veh_id)])

df = pd.DataFrame(data)
df.to_csv(output_path)

traci.close()
sys.stdout.flush()