import numpy as np
from scipy.spatial.transform import Rotation as R
import pandas as pd
import sys
from tqdm import tqdm

# Function to write PLY file
if len(sys.argv) < 2:
    print ("Please provide a ARposes txt file")
    sys.exit(1)
# Reading the data
arkit_dir = sys.argv[1]
gto_filename = arkit_dir +'/ARposes.g2o.out'  # Replace with your desired output path
adj_filename = arkit_dir +'/ARposes.adj.txt'

f_out = open(adj_filename, 'w')
f_out.write("Timestamp,Loc.x,Loc.y,Loc.z,Quat.w,Quat.x,Quat.y,Quat.z,TrackingStatus\n")

with open(gto_filename, 'r') as f:
    Lines = f.readlines()
    count = 0
    for line in tqdm(Lines):
        line_list = line.strip().split(' ')
        if(line_list[0] != "VERTEX_SE3:QUAT"):
            break

        f_out.write(str(line_list[1]) + "," + str(line_list[2]) + "," + str(line_list[3]) + "," + str(line_list[4]) + "," + str(line_list[8]) + "," + str(line_list[5]) + "," + str(line_list[6]) + "," + str(line_list[7]) + ",tracking\n")

