import numpy as np
from scipy.spatial.transform import Rotation as R
import pandas as pd
import sys
from tqdm import tqdm
import argparse
import logging

# create logger
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

def convert_g2o_to_arposes(gto_filename, arposes_filename):
    
    logging.info("Converting g2o to ARkit poses")
    f_out = open(arposes_filename, 'w')
    f_out.write("Timestamp,Loc.x,Loc.y,Loc.z,Quat.w,Quat.x,Quat.y,Quat.z,TrackingStatus\n")

    with open(gto_filename, 'r') as f:
        Lines = f.readlines()
        count = 0
        for line in tqdm(Lines):
            line_list = line.strip().split(' ')
            if(line_list[0] != "VERTEX_SE3:QUAT"):
                logging.info("Hit line that is not VERTEX_SE3:QUAT")
                break

            f_out.write(str(line_list[1]) + "," + str(line_list[2]) + "," + str(line_list[3]) + "," + str(line_list[4]) + "," + str(line_list[8]) + "," + str(line_list[5]) + "," + str(line_list[6]) + "," + str(line_list[7]) + ",Tracking\n")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ARKit poses to g2o format')
    parser.add_argument('--g2o', type=str, required=True, help='Path to input g2o file')
    parser.add_argument('--arposes', type=str, required=True, help='Path to output converted g2o file')
    args = parser.parse_args()

    input_gto_filename = args.g2o
    output_arposes_filename = args.arposes
    convert_g2o_to_arposes(input_gto_filename, output_arposes_filename)

    