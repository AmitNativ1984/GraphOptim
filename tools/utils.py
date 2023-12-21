import numpy as np
from scipy.spatial.transform import Rotation as R
import pandas as pd
import sys
from tqdm import tqdm
import argparse
import logging
import os

# create logger
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)


# Function to write PLY file
def write_g2o(filename, points, edges):
    logging.info("saving g2o graph to: {}".format(filename))
    with open(filename, 'w') as f:
        for ind, point in enumerate(points):
            f.write("VERTEX_SE3:QUAT {} {} {} {} {} {} {} {}\n".format(ind, point[0], point[1], point[2], point[3], point[4], point[5], point[6]))
        for edge in edges:
            f.write("EDGE_SE3:QUAT {} {} {} {} {} {} {} {} {} 100 0 0 0 0 0 100 0 0 0 0 100 0 0 0 100 0 0 100 0 100\n".format(edge[0], edge[1], edge[2], edge[3], edge[4], edge[5], edge[6], edge[7], edge[8]))

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


def arkittog2o(file_path):
    poses = pd.read_csv(file_path)
    poses.columns = ['Timestamp', 'X', 'Y', 'Z', 'QW', 'QX', 'QY', 'QZ', 'TrackingStatus']

    edges = list()
    logging.info("Converting AR kit to g2o") 
    for ind in tqdm(range(0, len(poses)-1), desc="Converted: "):
        r1 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind])
        r2 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind+1])
        r1 = r1.as_matrix()
        r2 = r2.as_matrix()
        rot_rel = r2 * r1.T
        q_rel = R.from_matrix(rot_rel).as_quat()

        t1 = poses[['X','Y','Z']].values[ind]
        t2 = poses[['X','Y','Z']].values[ind+1]
        t_rel = t2-t1
        edges.append([ind, ind+1,t_rel[0],t_rel[1],t_rel[2],q_rel[0],q_rel[1],q_rel[2],q_rel[3]])

    return poses, edges

def set_pairs_as_edges(poses, edges, pairs_file_path):
        
    pairs = pd.read_csv(pairs_file_path)
    pairs.columns = ['pose1','pose2']
    pair1 = pairs['pose1'].values
    pair2 = pairs['pose2'].values

    logging.info("Adding pairs as edges")

    for ind in tqdm(range(0, len(pairs)), desc="Pairs added: "):
        ind1 = pair1[ind]
        ind2 = pair2[ind]
        r1 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind1])
        r2 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind2])
        r1 = r1.as_matrix()
        r2 = r2.as_matrix()
        rot_rel = r2 * r1.T
        q_rel = R.from_matrix(rot_rel).as_quat()

        edges.append([ind1, ind2,0,0,0,q_rel[0],q_rel[1],q_rel[2],q_rel[3]])

    return edges

def convert_ARposes_to_ply(file_path):
    
    # get file_path without extension
    ply_filename = os.path.splitext(file_path)[0] + '.ply'
    logging.info("Converting ARposes to ply. Output file: {}".format(ply_filename))

    data = pd.read_csv(file_path)
    data.columns = ['Timestamp', 'X', 'Y', 'Z', 'QW', 'QX', 'QY', 'QZ', 'TrackingStatus']

    # Export to PLY
    write_ply(ply_filename, data[['X', 'Y', 'Z']].values)

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
    parser.add_argument('--arposes', type=str, required=True, help='Path to ARKit data folder')
    parser.add_argument('--pairs', type=str, required=True, help='Path to pairs.txt file')
    parser.add_argument('--g2o', type=str, required=True, help='Path to output g2o file')
    args = parser.parse_args()

    arposes_filename = args.arposes
    pairs_filename = args.pairs
    gto_filename = args.gto

    poses, edges = arkittog2o(arposes_filename, pairs_filename, gto_filename)
    edges = set_pairs_as_edges(poses, edges, pairs_filename)
    
    # Export to PLY
    write_g2o(gto_filename, poses[['X', 'Y', 'Z', 'QX', 'QY', 'QZ', 'QW']].values, edges)