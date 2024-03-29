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

#include "geometry/rotation.h"

#include <cmath>
#include <limits>

#include <Eigen/Geometry>

namespace gopt {

Eigen::Vector4d NormalizeQuaternion(const Eigen::Vector4d& quat) {
  Eigen::Vector4d normalized_quat;
  const double norm = quat.norm();
  if (norm == 0) {
    normalized_quat = Eigen::Vector4d(1.0, 0, 0, 0);
  } else {
    normalized_quat = quat / norm;
  }
  return normalized_quat;
}

Eigen::Vector3d RotationMatrixToAngleAxis(const Eigen::Matrix3d& R) {
  const Eigen::Vector4d quat = RotationMatrixToQuaternion(R);
  const Eigen::Vector4d normalized_quat = NormalizeQuaternion(quat);
  return QuaternionToAngleAxis(normalized_quat);
}

Eigen::Vector4d RotationMatrixToQuaternion(const Eigen::Matrix3d& R) {
  const Eigen::Quaterniond quat(R);
  return Eigen::Vector4d(quat.w(), quat.x(), quat.y(), quat.z());
}

Eigen::Matrix3d AngleAxisToRotationMatrix(const Eigen::Vector3d& angle_axis) {
  static const double kOne = 1.0;
  const double theta2 = angle_axis.squaredNorm();
  Eigen::Matrix3d R;

  // We want to be careful to only evaluate the square root if the
  // norm of the angle_axis vector is greater than zero. Otherwise
  // we get a division by zero.
  if (theta2 > std::numeric_limits<double>::epsilon()) {
    const double theta = angle_axis.norm();
    const double wx = angle_axis[0] / theta;
    const double wy = angle_axis[1] / theta;
    const double wz = angle_axis[2] / theta;

    const double costheta = std::cos(theta);
    const double sintheta = std::sin(theta);

    // The equation is derived from the Rodrigues formula.
    R(0, 0) = costheta + wx * wx * (kOne - costheta);
    R(1, 0) = wz * sintheta + wx * wy * (kOne - costheta);
    R(2, 0) = -wy * sintheta + wx * wz * (kOne - costheta);
    R(0, 1) = wx * wy * (kOne - costheta) - wz * sintheta;
    R(1, 1) = costheta + wy * wy * (kOne - costheta);
    R(2, 1) = wx * sintheta + wy * wz * (kOne - costheta);
    R(0, 2) = wy * sintheta + wx * wz * (kOne - costheta);
    R(1, 2) = -wx * sintheta + wy * wz * (kOne - costheta);
    R(2, 2) = costheta + wz * wz * (kOne - costheta);
  } else {
    // Near zero, we switch to using the first order Taylor expansion.
    R(0, 0) =  kOne;
    R(1, 0) =  angle_axis[2];
    R(2, 0) = -angle_axis[1];
    R(0, 1) = -angle_axis[2];
    R(1, 1) =  kOne;
    R(2, 1) =  angle_axis[0];
    R(0, 2) =  angle_axis[1];
    R(1, 2) = -angle_axis[0];
    R(2, 2) = kOne;
  }

  return R;
}

Eigen::Matrix3d QuaternionToRotationMatrix(const Eigen::Vector4d& quaternion) {
  Eigen::Vector4d normalized_quat = NormalizeQuaternion(quaternion);
  const Eigen::Quaterniond quat(normalized_quat[0], normalized_quat[1],
                                normalized_quat[2], normalized_quat[3]);
  return quat.toRotationMatrix();
}

Eigen::Vector3d QuaternionToAngleAxis(const Eigen::Vector4d& quat) {
  const Eigen::Vector4d normalized_quat = NormalizeQuaternion(quat);
  Eigen::Vector3d angle_axis;

  const double& qx = normalized_quat[1];
  const double& qy = normalized_quat[2];
  const double& qz = normalized_quat[3];
  // NOTE: quaternion should be normalized!
  const double sin_squared_theta = qx * qx + qy * qy + qz * qz;

  // For quaternions representing non-zero rotation, the conversion
  // is numerically stable.
  if (sin_squared_theta > 0.0) {
    const double sin_theta = std::sqrt(sin_squared_theta);
    const double& cos_theta = normalized_quat[0];

    // If cos_theta is negative, theta is greater than pi/2, which
    // means that angle for the angle_axis vector which is 2 * theta
    // would be greater than pi.
    //
    // While this will result in the correct rotation, it does not
    // result in a normalized angle-axis vector.
    //
    // In that case we observe that 2 * theta ~ 2 * theta - 2 * pi,
    // which is equivalent saying
    //
    //   theta - pi = atan(sin(theta - pi), cos(theta - pi))
    //              = atan(-sin(theta), -cos(theta))
    //
    const double two_theta =
        2.0 * ((cos_theta < 0.0)
                  ? std::atan2(-sin_theta, -cos_theta)
                  : std::atan2(sin_theta, cos_theta));
    const double k = two_theta / sin_theta;
    angle_axis[0] = qx * k;
    angle_axis[1] = qy * k;
    angle_axis[2] = qz * k;
  } else {
    // For zero rotation, sqrt() will produce NaN in the derivative since
    // the argument is zero.  By approximating with a Taylor series,
    // and truncating at one term, the value and first derivatives will be
    // computed correctly when Jets are used.
    const double k = 2.0;
    angle_axis[0] = qx * k;
    angle_axis[1] = qy * k;
    angle_axis[2] = qz * k;
  }
  return angle_axis;
}

Eigen::Vector4d AngleAxisToQuaternion(const Eigen::Vector3d& angle_axis) {
  Eigen::Vector4d quat;

  const double& a0 = angle_axis[0];
  const double& a1 = angle_axis[1];
  const double& a2 = angle_axis[2];
  const double theta_squared = angle_axis.squaredNorm();

  // For points not at the origin, the full conversion is numerically stable.
  if (theta_squared > 0.0) {
    const double theta = std::sqrt(theta_squared);
    const double half_theta = theta * 0.5;
    const double k = std::sin(half_theta) / theta;
    quat[0] = std::cos(half_theta);
    quat[1] = a0 * k;
    quat[2] = a1 * k;
    quat[3] = a2 * k;
  } else {
    // At the origin, sqrt() will produce NaN in the derivative since
    // the argument is zero.  By approximating with a Taylor series,
    // and truncating at one term, the value and first derivatives will be
    // computed correctly when Jets are used.
    const double k = 0.5;
    quat[0] = 1.0;
    quat[1] = a0 * k;
    quat[2] = a1 * k;
    quat[3] = a2 * k;
  }

  return quat;
}

double DotProduct(const Eigen::Vector3d& x, const Eigen::Vector3d& y) {
  return (x[0] * y[0] + x[1] * y[1] + x[2] * y[2]);
}

Eigen::Vector3d AngleAxisRotatePoint(const Eigen::Vector3d& angle_axis,
                                     const Eigen::Vector3d& pt) {
  Eigen::Vector3d result = Eigen::Vector3d::Zero();

  const double theta2 = DotProduct(angle_axis, angle_axis);
  if (theta2 > std::numeric_limits<double>::epsilon()) {
    // Away from zero, use the rodriguez formula
    //
    //   result = pt costheta +
    //            (w x pt) * sintheta +
    //            w (w . pt) (1 - costheta)
    //
    // We want to be careful to only evaluate the square root if the
    // norm of the angle_axis vector is greater than zero. Otherwise
    // we get a division by zero.
    //
    const double theta = sqrt(theta2);
    const double costheta = cos(theta);
    const double sintheta = sin(theta);
    const double theta_inverse = 1.0 / theta;

    const double w[3] = {angle_axis[0] * theta_inverse,
                    angle_axis[1] * theta_inverse,
                    angle_axis[2] * theta_inverse};

    // Explicitly inlined evaluation of the cross product for
    // performance reasons.
    const double w_cross_pt[3] = {
        w[1] * pt[2] - w[2] * pt[1],
        w[2] * pt[0] - w[0] * pt[2],
        w[0] * pt[1] - w[1] * pt[0]};
    const double tmp =
        (w[0] * pt[0] + w[1] * pt[1] + w[2] * pt[2]) * (1.0 - costheta);

    result[0] = pt[0] * costheta + w_cross_pt[0] * sintheta + w[0] * tmp;
    result[1] = pt[1] * costheta + w_cross_pt[1] * sintheta + w[1] * tmp;
    result[2] = pt[2] * costheta + w_cross_pt[2] * sintheta + w[2] * tmp;
  } else {
    // Near zero, the first order Taylor approximation of the rotation
    // matrix R corresponding to a vector w and angle theta is
    //
    //   R = I + hat(w) * sin(theta)
    //
    // But sintheta ~ theta and theta * w = angle_axis, which gives us
    //
    //  R = I + hat(angle_axis)
    //
    // and actually performing multiplication with the point pt, gives us
    // R * pt = pt + angle_axis x pt.
    //
    // Switching to the Taylor expansion near zero provides meaningful
    // derivatives when evaluated using Jets.
    //
    // Explicitly inlined evaluation of the cross product for
    // performance reasons.
    const double w_cross_pt[3] = {angle_axis[1] * pt[2] - angle_axis[2] * pt[1],
                             angle_axis[2] * pt[0] - angle_axis[0] * pt[2],
                             angle_axis[0] * pt[1] - angle_axis[1] * pt[0]};

    result[0] = pt[0] + w_cross_pt[0];
    result[1] = pt[1] + w_cross_pt[1];
    result[2] = pt[2] + w_cross_pt[2];
  }

  return result;
}

}  // namespace gopt
