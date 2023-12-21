import numpy as np
import pandas as pd
import sys

# Function to write PLY file
def write_ply(filename, points):
    with open(filename, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("element vertex {}\n".format(len(points)))
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")
        for point in points:
            f.write("{} {} {}\n".format(point[0], point[1], point[2]))

if len(sys.argv) < 1:
    print ("Please provide a ARposes txt file")
    sys.exit(1)
# Reading the data
file_path = sys.argv[1] #"/DATA/ITG/ios_logger_noDepth/2023-11-27T09-37-23-small/ARposes.txt"  # Replace with the path to your file
ply_filename = file_path+'.ply'  # Replace with your desired output path

data = pd.read_csv(file_path)
data.columns = ['Timestamp', 'X', 'Y', 'Z', 'Value1', 'Value2', 'Value3', 'Value4', 'TrackingStatus']

# Calculate the range for each axis
max_range = np.array([data['X'].max()-data['X'].min(), 
                      data['Y'].max()-data['Y'].min(), 
                      data['Z'].max()-data['Z'].min()]).max() / 2.0

# Find the center point for each axis
mid_x = (data['X'].max()+data['X'].min()) * 0.5
mid_y = (data['Y'].max()+data['Y'].min()) * 0.5
mid_z = (data['Z'].max()+data['Z'].min()) * 0.5

# Export to PLY
write_ply(ply_filename, data[['X', 'Y', 'Z']].values)


