#建议搭配33.mp4演示
import PySimpleGUI as sg  # 引入图形界面库
import cv2  # 引入OpenCV库用于图像处理
import numpy as np  # 引入numpy库用于数值计算
import time  # <--- 新增：用于精准控制帧率延迟

# 设置主题颜色为浅灰色
sg.theme('LightGrey')

# 初始化变量
start = False  # 控制视频播放标志
pause = False  # 控制视频暂停标志
cap = None  # 视频捕获对象
mouse_clicked = False  # 标记是否已点击鼠标
center_pos = (0, 0)  # 保存鼠标点击的位置作为采样框中心

# 定义图像和图表的大小以及采样的步长和数量
IMAGE_SIZE = (550, 300)
STEP_SIZE = 1
SAMPLES = 100
SAMPLE_MAX = 100
CANVAS_SIZE = (500, 100)
TOTAL_COUNT_GRAPH_SIZE = (500, 100)  # 新增总计数图表的大小定义

# 初始化用于图形绘制的数据
i = 0
prev_x, prev_y = 0, 0
graph_value = 0
counter_right = 0
counter_left = 0
check_value = 0
last_direction = None
gray_diff_history = []  # 存储灰度差值的历史数据
avg_gray_history = []  # 存储整个采样框平均灰度值的历史数据
avg_gray_rising = None  # 用于记录avg_gray上升趋势
avg_gray_falling = None  # 用于记录avg_gray下降趋势
total_count_history = []  # 新增存储总计数历史数据的列表

# 定义窗口布局元素
layout = [
    # 主要图像显示区
    [sg.Image(filename='', key='image', size=IMAGE_SIZE)],

    # ================= 修改布局：使用 Column 和 Push 实现完美对齐 =================
    [
        sg.Push(),  # 将后面的元素整体向右推，实现右侧对齐
        sg.Frame('', [[sg.Image(filename='', key='cut_image')]]),  # 给切割图像加个边框
        sg.Column([[sg.Frame('灰度差(红) / 平均灰度(蓝)', [
                [sg.Graph(CANVAS_SIZE, (0, -SAMPLE_MAX), (SAMPLES, SAMPLE_MAX),
                          background_color='black', key='graph')]])],
            [sg.Frame('总计数趋势(绿)', [
                [sg.Graph(TOTAL_COUNT_GRAPH_SIZE, (0, -SAMPLE_MAX), (SAMPLES, SAMPLE_MAX),
                background_color='black', key='total_count_graph')]])]], vertical_alignment='center')  # 【关键修改】：这里改为 'center' 实现垂直中心对齐
    ],
    # 文件浏览按钮和输入框
    [sg.Text('选择视频文件', size=(10, 1)), sg.Input(key='video_path', size=(50, 1),default_text='video/33.mp4'), sg.FileBrowse()],
    # 采样框大小调整滑块
    [sg.Text('采样框', size=(8, 1)),
     sg.Slider((0, 1000), 202, 1, orientation='h', size=(16, 15), key='rectangle_a'),
     sg.Slider((0, 1000), 645, 1, orientation='h', size=(16, 15), key='rectangle_b'),
     sg.Slider((0, 100), 30, 1, orientation='h', size=(14, 15), key='rectangle_l')],
    # 阈值调整滑块
    [sg.Text('阈值二值化', size=(8, 1), visible=False),
     sg.Slider((0, 255), 170, 1, orientation='h', size=(48, 15), key='thresh_slider', visible=False)],
    # 对比度调整滑块
    [sg.Text('对比度', size=(8, 1)),
     sg.Slider((1, 255), 105, 1, orientation='h', size=(22, 15), key='enhance_slider'), sg.Text('基线'),
     sg.Slider((1, 100), 80, 1, orientation='h', size=(21, 15), key='check_slider')],

    # 显示条纹移动的数量
    [sg.Text('从左向右（吞）条纹移动的个数：0', key='count_right'), sg.Text('个', size=(4, 1)) , sg.Text('从右向左（吐）条纹移动的个数：0', key='count_left'), sg.Text('个', size=(4, 1))],
    [sg.Column([[sg.Text('总计数：0', key='total_count')]], expand_x=True, element_justification='left'),
        sg.Column([[sg.Text('左右差值: ', key='gray_diff'), sg.Text('0', key='diff_value')]], expand_x=True,
                  element_justification='left')],
    # 按钮行
    [sg.Button('重置', size=(9, 1)), sg.Button('开始', size=(9, 1)), sg.Button('暂停', size=(9, 1)),
     sg.Button('停止', size=(9, 1)), sg.Button('退出', size=(8, 1))]
]

# 创建窗口
window = sg.Window('条纹计数系统', layout, finalize=True)

# 主循环
while True:
    event, values = window.read(timeout=1)  # 获取事件和值

    if event == '开始':  # 开始播放视频
        video_path = values['video_path']
        if video_path:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                start = True
                pause = False  # 开始播放时取消暂停状态
                # --- 新增：获取视频真实帧率并计算每帧需要等待的时间 ---
                video_fps = cap.get(cv2.CAP_PROP_FPS)
                if video_fps <= 0:
                    video_fps = 30.0  # 默认 fallback 到 30 FPS
                frame_delay = 1.0 / video_fps  # 每帧应该花费的秒数 (例如 30fps -> 0.033秒)
                # ----------------------------------------------------

    if event == '停止':  # 停止播放视频
        start = False
        pause = False  # 停止播放时也取消暂停状态
        if cap is not None:
            cap.release()
            cap = None

    if event == '重置':  # 重置计数器并清除图表
        counter_right = 0
        counter_left = 0
        total_count = 0
        window['graph'].erase()
        window['total_count_graph'].erase()  # 清除总计数图表
        gray_diff_history.clear()
        avg_gray_history.clear()
        total_count_history.clear()  # 清除总计数历史数据
        avg_gray_rising = None
        avg_gray_falling = None
        window['count_right'].update('从左向右（吞）条纹移动的个数：0')
        window['count_left'].update('从右向左（吐）条纹移动的个数：0')
        window['total_count'].update('总计数：0')  # 重置总计数显示

    if event == '暂停':  # 暂停播放视频
        pause = not pause

    if event == '退出' or event is None:  # 退出程序
        break

    if not start:  # 如果没有开始，则跳过后续处理
        continue

    if cap is not None:  # 如果视频捕获对象有效，则读取帧
        if not pause:  # 只有在未暂停的情况下才读取新帧
            # --- 新增：记录处理开始时间，用于帧率同步 ---
            start_time = time.time()
            ret, frame = cap.read()
            if ret:
                new_frame = frame

                # 提升对比度
                enh_val = values['enhance_slider'] / 40
                clahe = cv2.createCLAHE(clipLimit=enh_val, tileGridSize=(8, 8))
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                lab[:, :, 0] = clahe.apply(lab[:, :, 0])
                frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.threshold(frame, values['thresh_slider'], 255, cv2.THRESH_BINARY)[1]

                # 使用鼠标点击的位置作为采样框的中心
                if mouse_clicked:
                    x, y = center_pos[0], center_pos[1]
                    mouse_clicked = False
                else:
                    x, y = int(values['rectangle_a']), int(values['rectangle_b'])

                l = int(values['rectangle_l'])
                x1, y1 = x + l, y + l
                new_frame = cv2.rectangle(new_frame, (x, y), (x1, y1), (0, 0, 255), cv2.LINE_4, 2)

                # 提取采样框内的图像
                cut_frame = frame[y:y1, x:x1]
                if cut_frame.size:
                    # 计算整个采样框的平均灰度值
                    avg_gray = np.mean(cut_frame) // 4

                    # 将采样框内图像分为左右两部分
                    half_l = l // 2
                    left_cut = cut_frame[:, :half_l]
                    right_cut = cut_frame[:, half_l:]

                    # 计算左右两侧的平均灰度值
                    left_avg = np.mean(left_cut)
                    right_avg = np.mean(right_cut)

                    # 计算左右两侧的平均灰度值差
                    gray_diff = (left_avg - right_avg) / 2

                    # 更新灰度差值显示
                    window['diff_value'].update(f'{gray_diff:.2f}')

                    # 更新灰度差值历史数据
                    gray_diff_history.append(gray_diff)
                    if len(gray_diff_history) > SAMPLES:
                        gray_diff_history.pop(0)

                    # 更新整个采样框的平均灰度值历史数据
                    avg_gray_history.append(avg_gray)
                    if len(avg_gray_history) > SAMPLES:
                        avg_gray_history.pop(0)

                    # 更新切割区域的图像
                    cutimgbytes = cv2.imencode('.png', cut_frame)[1].tobytes()
                    window['cut_image'].update(data=cutimgbytes)

                    # 更新图表
                    graph = window['graph']
                    if check_value != int(values['check_slider']):
                        check_value = int(values['check_slider'])
                        graph.erase()
                    graph.draw_line((-SAMPLE_MAX, check_value), (SAMPLE_MAX, check_value), color='white')

                    # 清除旧的线条
                    graph.erase()
                    # 绘制 0 值的参考线
                    graph.draw_line((0, 0), (SAMPLES, 0), color='white')

                    # 绘制新的灰度差值图表
                    for idx, diff in enumerate(gray_diff_history):
                        graph.draw_point((idx, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(diff)))), color='red')
                        if idx > 0:
                            graph.draw_line((idx-1, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(prev_diff)))),
                                            (idx, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(diff)))), color='red')
                        prev_diff = diff

                    # 绘制平均灰度值图表
                    for idx, avg_gray in enumerate(avg_gray_history):
                        graph.draw_point((idx, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(avg_gray)))), color='blue')
                        if idx > 0:
                            graph.draw_line((idx-1, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(prev_avg_gray)))),
                                            (idx, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(avg_gray)))), color='blue')
                        prev_avg_gray = avg_gray

                    # 更新总计数历史数据
                    total_count = (counter_right - counter_left)*20
                    total_count_history.append(total_count)
                    if len(total_count_history) > SAMPLES:
                        total_count_history.pop(0)

                    # 更新总计数图表
                    total_count_graph = window['total_count_graph']
                    total_count_graph.erase()
                    for idx, count in enumerate(total_count_history):
                        if idx > 0 :
                            total_count_graph.draw_line((idx-1, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(prev_total_count)))),
                                                        (idx, min(SAMPLE_MAX, max(-SAMPLE_MAX, int(count)))), color='green')
                        prev_total_count = count

                    # 更新计数逻辑
                    if len(gray_diff_history) >= 2:
                        if gray_diff_history[-1] < 40 and gray_diff_history[-2] > 40:
                            # 检测到从峰值（大于40）到谷值（小于40）的变化
                            if avg_gray_falling and not avg_gray_rising:
                                # 如果avg_gray先前是在下降，现在开始上升，则条纹从右向左移动
                                counter_left += 1
                                avg_gray_falling = None  # 重置趋势标记
                                avg_gray_rising = True
                            elif avg_gray_rising and not avg_gray_falling:
                                # 如果avg_gray先前是在上升，现在开始下降，则条纹从左向右移动
                                counter_right += 1
                                avg_gray_rising = None  # 重置趋势标记
                                avg_gray_falling = True

                    # 更新avg_gray的趋势
                    if len(avg_gray_history) >= 2:
                        if avg_gray_history[-1] > avg_gray_history[-2]:
                            avg_gray_rising = True
                            avg_gray_falling = False
                        elif avg_gray_history[-1] < avg_gray_history[-2]:
                            avg_gray_falling = True
                            avg_gray_rising = False

                    # 更新计数显示
                    window['count_right'].update('从左向右（吞）条纹移动的个数：' + str(counter_right))
                    window['count_left'].update('从右向左（吐）条纹移动的个数：' + str(counter_left))

                    # 计算并更新总计数
                    total_count = counter_right - counter_left
                    window['total_count'].update('总计数：' + str(total_count))

                # 更新主要图像
                imgbytes = cv2.imencode('.png', new_frame)[1].tobytes()
                window['image'].update(data=imgbytes, size=IMAGE_SIZE)

window.close()  # 关闭窗口
