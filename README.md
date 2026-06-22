# 🔬 InterFringe-Analyzer (干涉条纹分析监测系统)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv" alt="OpenCV">
  <img src="https://img.shields.io/badge/Application-地震监测模拟-orange" alt="Application">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 📖 项目简介

**InterFringe-Analyzer** 是一套基于计算机视觉的干涉条纹实时分析系统。本项目创新性地**将迈克尔逊干涉仪与光学摄像头相结合，通过监测干涉条纹的微小移动，模拟地震监测仪对地表微振动的响应过程**。

当实验平台或反射镜受到外界微小扰动（如模拟地震波）时，光程差发生改变，导致干涉条纹移动。本程序通过提取视频画面中局部区域的灰度特征，精准判定条纹的移动方向（“吞”或“吐”）并统计变化次数，从而定量反映外界扰动引起的光程差变化。

> 💡 **适用场景**：大学物理创新实验、光学干涉现象演示、数字图像处理课程设计，以及“用光学方法模拟地震监测”的跨学科实验展示。

## ✨ 核心特性

- 🎥 **实时视频流分析**：支持加载本地实验录像，并根据视频真实帧率进行精准同步播放与分析。
- 🖼️ **自适应图像增强**：集成 **CLAHE (对比度受限自适应直方图均衡化)** 算法，动态调节对比度，有效克服实验室光照不均导致的条纹模糊问题。
- 🎯 **灵活的 ROI 采样**：支持通过 GUI 滑块或鼠标交互，实时调整采样框的位置与大小，精准锁定条纹最清晰的区域。
- 🧠 **智能方向判定算法**：摒弃简单的像素比对，采用 **“左右灰度差分 + 整体灰度趋势追踪”** 的双重校验机制，精准区分条纹移动方向。
- 📊 **多维数据可视化**：
  - 🔴 **红曲线**：采样框左右半区灰度差值（捕捉条纹周期的核心指标）。
  - 🔵 **蓝曲线**：采样框整体平均灰度值（辅助判定移动方向）。
  - 🟢 **绿曲线**：总计数值（净光程差变化）趋势图。

## 🛠️ 技术栈

| 技术/库 | 用途说明 |
| --- | --- |
| **Python 3.9+** | 核心开发语言 |
| **OpenCV (`cv2`)** | 视频解码、CLAHE 对比度增强、灰度化、二值化、ROI 裁剪 |
| **NumPy** | 矩阵运算与灰度均值高效计算 |
| **PySimpleGUI** | 构建轻量级、响应式的桌面图形用户界面 (GUI) |

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/2796199964-cmyk/InterFringe-Analyzer.git
cd InterFringe-Analyzer
