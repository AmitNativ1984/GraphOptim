// BSD 3-Clause License

// Copyright (c) 2021, Chenyu
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.

// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.

// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from
//    this software without specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "graph/view_graph.h"

#include <string>

#include <glog/logging.h>
#include <gflags/gflags.h>

#include "utils/types.h"

DEFINE_string(g2o_filename, "", "The absolute path of g2o file");

int main(int argc, char* argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, false);

  google::InitGoogleLogging(argv[0]);
  FLAGS_alsologtostderr = true;
  FLAGS_colorlogtostderr = true;

  if (argc < 2) {
    LOG(INFO) << "[Usage]: rotation_estimator --g2o_filename=g2o_filename";
    return 0;
  }

  std::string g2o_filename = FLAGS_g2o_filename;
  std::string g2o_filename_out = g2o_filename + ".out";

  gopt::graph::ViewGraph view_graph;
  view_graph.ReadG2OFile(g2o_filename);

  // gopt::RotationEstimatorOptions options;
  // options.sdp_solver_options.verbose = true;
  
  // // Set to 1e-6 for se-sync datasets.
  // options.sdp_solver_options.tolerance = 1e-8;
  // options.sdp_solver_options.max_iterations = 100;
  // options.sdp_solver_options.riemannian_staircase_options.
  //     min_eigenvalue_nonnegativity_tolerance = 1e-2;
  // options.Setup();
  
  // std::unordered_map<gopt::image_t, Eigen::Vector3d> global_rotations;
  // view_graph.RotationAveraging(options, &global_rotations);

  gopt::PositionEstimatorOptions options_r;
  options_r.verbose = true;

  std::unordered_map<gopt::image_t, Eigen::Vector3d> global_positions;
  view_graph.TranslationAveraging(options_r, &global_positions);
  LOG(INFO) << "saved data to: " << g2o_filename_out;
  view_graph.WriteG2OFile(g2o_filename_out);
}
