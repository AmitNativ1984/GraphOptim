# Use Ubuntu 22.04 (will be supported until April 2027)
FROM ubuntu:jammy as dev

RUN DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libeigen3-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    libcgal-qt5-dev

##########################
## INSTALL CERES-SOLVER ##
##########################
WORKDIR /installs 
RUN git clone --branch 1.14.x https://github.com/ceres-solver/ceres-solver.git \
    && cd ceres-solver \
    # Latest release of ceres not provides FindEigen3.cmake
    && mkdir build && cd build \
    && cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF \
    && make -j8 \
    && make install 

####################
## INSTALL COLMAP ##
####################
RUN git clone https://github.com/AIBluefisher/colmap.git \
    && cd colmap \
    && git checkout dev \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j8 \
    && make install 
    
####################
RUN apt-get install -y python3-pip
RUN pip3 install \
    numpy \
    scipy \
    pandas \
    matplotlib \
    pyproj \
    opencv-python \
    moviepy
   

###################
### BUILD STAGE ###
###################
FROM dev as release

COPY . /app
WORKDIR /app
RUN mkdir build && cd build && cmake .. && make -j8

CMD ["/bin/bash"]



