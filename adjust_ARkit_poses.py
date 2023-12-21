import argparse
from tools.utils import *
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ARKit poses to g2o format')
    parser.add_argument('--arposes', type=str, required=True, help='Path to ARKit data folder')
    parser.add_argument('--pairs', type=str, required=True, help='Path to pairs.txt file')
    args = parser.parse_args()

    arposes_filename = args.arposes
    pairs_filename = args.pairs
    
    g2o_filename = os.path.splitext(arposes_filename)[0] + '.g2o'

    # step 1: convert ARkit poses to g2o format   
    poses, edges = arkittog2o(arposes_filename)
    
    #step 2: add pairs as edges
    edges = set_pairs_as_edges(poses, edges, pairs_filename)
    
    #step 3: create and save g2o file
    write_g2o(g2o_filename, poses[['X', 'Y', 'Z', 'QX', 'QY', 'QZ', 'QW']].values, edges)

    #step 4: run graph translation optimization
    pGraphOptim = subprocess.Popen(['bin/position_estimator', "--g2o_filename={}".format(g2o_filename)])
    pGraphOptim.wait()

    #step 5: convert g2o back to ARkit poses
    g2o_output_filename = g2o_filename + '.out'
    output_arposes_filename = os.path.splitext(g2o_filename)[0] + '.adj' + '.txt'
    convert_g2o_to_arposes(g2o_output_filename, output_arposes_filename)

    #step 6: convert ARkit poses to ply
    convert_ARposes_to_ply(output_arposes_filename)

