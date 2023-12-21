import numpy as np
import pandas as pd
import sys
import argparse
import os
import logging

# create logger
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

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


def convert_ARposes_to_ply(file_path):
    
    # get file_path without extension
    ply_filename = os.path.splitext(file_path)[0] + '.ply'
    logging.info("Converting ARposes to ply. Output file: {}".format(ply_filename))

    data = pd.read_csv(file_path)
    data.columns = ['Timestamp', 'X', 'Y', 'Z', 'QW', 'QX', 'QY', 'QZ', 'TrackingStatus']

    # Export to PLY
    write_ply(ply_filename, data[['X', 'Y', 'Z']].values)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ARKit poses to g2o format')
    parser.add_argument('--arposes', type=str, required=True, help='Path to ARKit data folder')
    args = parser.parse_args()

    arposes_file = args.arposes
    
    convert_ARposes_to_ply(arposes_file)

