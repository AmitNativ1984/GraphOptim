import argparse
from tools.utils import *
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ARKit poses to g2o format')
    parser.add_argument('--arposes', type=str, required=True, help='Path to ARKit data folder')
    args = parser.parse_args()

    arposes_filename = args.arposes
    
    convert_ARposes_to_ply(arposes_filename)