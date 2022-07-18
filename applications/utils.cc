#include "utils.h"

#include <glog/logging.h>

#include <colmap/base/database.h>
#include <colmap/feature/types.h>

namespace gopt {

void LoadTracksFromDB(
    const std::string& database_path,
    TrackElements* track_elements,
    std::vector<std::pair<track_t, track_t>>* track_element_pairs) {
  colmap::Database database(database_path);
  LOG(INFO) << "Loading tracks...";
  std::vector<colmap::TwoViewGeometry> two_view_geometries;
  std::vector<image_pair_t> image_pair_ids;

  database.ReadTwoViewGeometries(&image_pair_ids, &two_view_geometries);

  std::unordered_map<std::string, size_t> track_key_to_idx;

  // #pragma omp parallel for
  for (size_t i = 0; i < image_pair_ids.size(); i++) {
    image_t image_id1;
    image_t image_id2;
    colmap::Database::PairIdToImagePair(image_pair_ids[i], &image_id1, &image_id2);

    const colmap::TwoViewGeometry& two_view_geometry = two_view_geometries[i];
    const auto& inlier_matches = two_view_geometry.inlier_matches;

    for (const colmap::FeatureMatch& match : inlier_matches) {
      const point2D_t point2d_idx1 = match.point2D_idx1;
      const point2D_t point2d_idx2 = match.point2D_idx2;
      const TrackElement track_element1(image_id1, point2d_idx1);
      const TrackElement track_element2(image_id2, point2d_idx2);

      const std::string track_key1 =
          std::to_string(image_id1) + "_" + std::to_string(point2d_idx1);
      const std::string track_key2 =
          std::to_string(image_id2) + "_" + std::to_string(point2d_idx2);

      if (track_key_to_idx.count(track_key1) == 0) {
        track_key_to_idx[track_key1] = track_key_to_idx.size();
        track_elements->emplace_back(track_element1);
      }
      
      if (track_key_to_idx.count(track_key2) == 0) {
        track_key_to_idx[track_key2] = track_key_to_idx.size();
        track_elements->emplace_back(track_element2);
      }

      const track_t track_id1 = track_key_to_idx.at(track_key1);
      const track_t track_id2 = track_key_to_idx.at(track_key2);
      track_element_pairs->emplace_back(track_id1, track_id2);
    }
  }
}

}  // namespace gopt
