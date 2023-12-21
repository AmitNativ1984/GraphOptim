import numpy as np
from scipy.spatial.transform import Rotation as R
import pandas as pd
import sys
from tqdm import tqdm

# Function to write PLY file
def write_g2o(filename, points, edges):
    with open(filename, 'w') as f:
        for ind, point in enumerate(points):
            f.write("VERTEX_SE3:QUAT {} {} {} {} {} {} {} {}\n".format(ind, point[0], point[1], point[2], point[3], point[4], point[5], point[6]))
        for edge in edges:
            f.write("EDGE_SE3:QUAT {} {} {} {} {} {} {} {} {} 100 0 0 0 0 0 100 0 0 0 0 100 0 0 0 100 0 0 100 0 100\n".format(edge[0], edge[1], edge[2], edge[3], edge[4], edge[5], edge[6], edge[7], edge[8]))

if len(sys.argv) < 2:
    print ("Please provide a ARposes txt file")
    sys.exit(1)
# Reading the data
arkit_dir = sys.argv[1]
file_path = arkit_dir + "/ARposes.txt" 
pairs_file_path = arkit_dir + "/pairs.txt" 
gto_filename = arkit_dir +'/ARposes.g2o'  # Replace with your desired output path

poses = pd.read_csv(file_path)
poses.columns = ['Timestamp', 'X', 'Y', 'Z', 'QW', 'QX', 'QY', 'QZ']

edges = list()
# for ind in tqdm(range(0, len(poses)-1)):
#     r1 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind])
#     r2 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind+1])
#     r1 = r1.as_matrix()
#     r2 = r2.as_matrix()
#     r1 = np.vstack((np.array(r1), np.array([poses[['X','Y','Z']].values[ind]])))
#     r1 = np.hstack((r1, np.array([[0],[0],[0],[1]])))
#     r2 = np.vstack((r2, np.array([poses[['X','Y','Z']].values[ind+1]])))
#     r2 = np.hstack((r2, np.array([[0],[0],[0],[1]])))
#     rt_rel = r2 * r1.T
#     rot_rel = rt_rel[0:3,0:3]
#     q_rel = R.from_matrix(rot_rel).as_quat()
#     t_rel = rt_rel[3,0:3]
#     edges.append([ind, ind+1,t_rel[0],t_rel[1],t_rel[2],q_rel[0],q_rel[1],q_rel[2],q_rel[3]])

for ind in tqdm(range(0, len(poses)-1)):
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

pairs = pd.read_csv(pairs_file_path)
pairs.columns = ['pose1','pose2']
pair1 = pairs['pose1'].values
pair2 = pairs['pose2'].values
    
for ind in tqdm(range(0, len(pairs))):
    ind1 = pair1[ind]
    ind2 = pair2[ind]
    r1 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind1])
    r2 = R.from_quat(poses[['QX', 'QY', 'QZ', 'QW']].values[ind2])
    r1 = r1.as_matrix()
    r2 = r2.as_matrix()
    rot_rel = r2 * r1.T
    q_rel = R.from_matrix(rot_rel).as_quat()

    edges.append([ind1, ind2,0,0,0,q_rel[0],q_rel[1],q_rel[2],q_rel[3]])


# Export to PLY
write_g2o(gto_filename, poses[['X', 'Y', 'Z', 'QX', 'QY', 'QZ', 'QW']].values, edges)


