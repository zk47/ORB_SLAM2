#include <iostream>
#include <algorithm>
#include <fstream>
#include <chrono>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "System.h"

using namespace std;

// 处理图像和SLAM跟踪的函数，将在子线程中运行
void ProcessImages(ORB_SLAM2::System* pSLAM, const string& strAssociationFilename, const string& strSequencePath)
{
    // 读取关联文件
    ifstream fAssociation;
    fAssociation.open(strAssociationFilename.c_str());
    vector<string> vstrImageFilenamesRGB;
    vector<string> vstrImageFilenamesD;
    vector<double> vTimestamps;

    while (!fAssociation.eof())
    {
        string s;
        getline(fAssociation, s);
        if (!s.empty())
        {
            stringstream ss;
            ss << s;
            double t;
            string sRGB, sD;
            ss >> t >> sRGB >> t >> sD;
            vTimestamps.push_back(t);
            vstrImageFilenamesRGB.push_back(strSequencePath + "/" + sRGB);
            vstrImageFilenamesD.push_back(strSequencePath + "/" + sD);
        }
    }

    // 检查图像数量是否匹配
    int nImages = vstrImageFilenamesRGB.size();
    if (vstrImageFilenamesRGB.empty())
    {
        cerr << endl << "No images found in provided path." << endl;
        return;
    }
    else if (vstrImageFilenamesD.size() != vstrImageFilenamesRGB.size())
    {
        cerr << endl << "Number of RGB and depth images do not match." << endl;
        return;
    }

    // 处理所有图像
    cv::Mat imRGB, imD;
    for (int ni = 0; ni < nImages; ni++)
    {
        // 读取图像
        imRGB = cv::imread(vstrImageFilenamesRGB[ni], cv::IMREAD_UNCHANGED);
        imD = cv::imread(vstrImageFilenamesD[ni], cv::IMREAD_UNCHANGED);
        double tframe = vTimestamps[ni];

        if (imRGB.empty())
        {
            cerr << endl << "Failed to load image at: " << vstrImageFilenamesRGB[ni] << endl;
            return;
        }

        // 在SLAM系统中跟踪当前帧
        pSLAM->TrackRGBD(imRGB, imD, tframe);

        // 按ESC键退出
        char c = (char)cv::waitKey(1);
        if (c == 27)
            break;
    }
}

int main(int argc, char **argv)
{
    if (argc != 5)
    {
        cerr << endl << "Usage: ./rgbd_tum path_to_vocabulary path_to_settings path_to_sequence path_to_association" << endl;
        return 1;
    }

    // 初始化ORB-SLAM2系统
    ORB_SLAM2::System SLAM(argv[1], argv[2], ORB_SLAM2::System::RGBD, false); // 禁用内部Viewer线程

    // 启动图像处理子线程
    thread processingThread(ProcessImages, &SLAM, argv[4], argv[3]);

    // 主线程运行Viewer
    SLAM.RunViewer();

    // 等待处理线程完成
    processingThread.join();

    // 关闭SLAM系统
    SLAM.Shutdown();

    // 保存轨迹
    SLAM.SaveTrajectoryTUM("CameraTrajectory.txt");
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");

    return 0;
}