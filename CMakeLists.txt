cmake_minimum_required(VERSION 3.10)
project(ORB_SLAM2)

# 设置构建类型为Release（若未指定）
IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Release)
ENDIF()

MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})

# 基础编译选项（开启警告和优化）
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")

# 检查C++14/11支持（优先使用C++14以兼容Pangolin依赖）
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)

if(COMPILER_SUPPORTS_CXX14)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
   add_definitions(-DCOMPILEDWITHC14)
   message(STATUS "Using flag -std=c++14.")
elseif(COMPILER_SUPPORTS_CXX11)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
   add_definitions(-DCOMPILEDWITHC11)
   message(STATUS "Using flag -std=c++11.")
elseif(COMPILER_SUPPORTS_CXX0X)
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
   add_definitions(-DCOMPILEDWITHC0X)
   message(STATUS "Using flag -std=c++0x.")
else()
   message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++14 support. Please use a different C++ compiler.")
endif()

# 添加CMake模块搜索路径
LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

# 设置第三方库路径（根据实际安装位置调整）
list(APPEND CMAKE_PREFIX_PATH "/opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4")
list(APPEND CMAKE_PREFIX_PATH "/opt/homebrew/lib/cmake/Pangolin")

# 查找OpenCV（兼容4.x和2.4.x）
find_package(OpenCV 4.0 QUIET)
if(NOT OpenCV_FOUND)
   find_package(OpenCV 2.4.3 QUIET)
   if(NOT OpenCV_FOUND)
      message(FATAL_ERROR "OpenCV > 2.4.3 not found.")
   endif()
endif()

# 查找Eigen3并手动创建目标（解决Pangolin依赖问题）
find_package(Eigen3 3.4.0 REQUIRED)
if(NOT TARGET Eigen3::Eigen)
  # 手动创建Eigen3::Eigen目标供Pangolin使用
  add_library(Eigen3::Eigen INTERFACE IMPORTED)
  set_target_properties(Eigen3::Eigen PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}"
  )
endif()

if(NOT EIGEN3_FOUND)
   message(FATAL_ERROR "Eigen3 not found.")
else()
   message(STATUS "Eigen3 is found. Include dir: ${EIGEN3_INCLUDE_DIR}")
   # 确保Pangolin能识别Eigen3路径
   #set(Eigen3_DIR ${EIGEN3_DIR} CACHE PATH "" FORCE)
   #list(APPEND CMAKE_PREFIX_PATH ${EIGEN3_DIR})
      # 强制设置Eigen3的CMake配置路径（关键！让Pangolin能找到）
   set(Eigen3_DIR "/opt/homebrew/share/eigen3/cmake" CACHE PATH "Eigen3 CMake config directory" FORCE)
   list(APPEND CMAKE_PREFIX_PATH ${Eigen3_DIR})
endif()

# 查找Pangolin
find_package(Pangolin REQUIRED)

# 包含头文件目录
include_directories(
${PROJECT_SOURCE_DIR}
${PROJECT_SOURCE_DIR}/include
${EIGEN3_INCLUDE_DIR}
${Pangolin_INCLUDE_DIRS}
${OpenCV_INCLUDE_DIRS}
)

# 设置库输出目录
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

# 构建ORB_SLAM2核心库
add_library(${PROJECT_NAME} SHARED
src/System.cc
src/Tracking.cc
src/LocalMapping.cc
src/LoopClosing.cc
src/ORBextractor.cc
src/ORBmatcher.cc
src/FrameDrawer.cc
src/Converter.cc
src/MapPoint.cc
src/KeyFrame.cc
src/Map.cc
src/MapDrawer.cc
src/Optimizer.cc
src/PnPsolver.cc
src/Frame.cc
src/KeyFrameDatabase.cc
src/Sim3Solver.cc
src/Initializer.cc
src/Viewer.cc
)

# 链接依赖库
target_link_libraries(${PROJECT_NAME}
${OpenCV_LIBS}
Eigen3::Eigen  # 链接Eigen3目标
${Pangolin_LIBRARIES}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/lib/libDBoW2.dylib
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.dylib
)

# 构建示例程序 - RGB-D
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)
add_executable(rgbd_tum Examples/RGB-D/rgbd_tum.cc)
target_link_libraries(rgbd_tum ${PROJECT_NAME})

# 构建示例程序 - Stereo
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo)
add_executable(stereo_kitti Examples/Stereo/stereo_kitti.cc)
target_link_libraries(stereo_kitti ${PROJECT_NAME})

add_executable(stereo_euroc Examples/Stereo/stereo_euroc.cc)
target_link_libraries(stereo_euroc ${PROJECT_NAME})

# 构建示例程序 - Monocular
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular)
add_executable(mono_tum Examples/Monocular/mono_tum.cc)
target_link_libraries(mono_tum ${PROJECT_NAME})

add_executable(mono_kitti Examples/Monocular/mono_kitti.cc)
target_link_libraries(mono_kitti ${PROJECT_NAME})

add_executable(mono_euroc Examples/Monocular/mono_euroc.cc)
target_link_libraries(mono_euroc ${PROJECT_NAME})
