import sys
import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox, QComboBox, QDesktopWidget, QDialog, QLabel, QDialogButtonBox
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from course_widget import CourseWidget  # 导入CourseWidget

class CourseScheduleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.show_delete_button = self.check_delete_button_status()
        
        # 获取今天的星期数并初始化课程数据
        self.today_weekday = QDate.currentDate().dayOfWeek()
        self.current_weekday = self.today_weekday
        self.courses = self.loadCoursesFromFile(self.today_weekday)
        
        # 设置开机自启动
        self.setup_autostart()
        
        # 初始化UI
        self.initUI()
        self.moveToRightTop()

    def calculateWindowSize(self):
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        screen_height = screen.height()
        screen_width = screen.width()
        
        # 根据显示模式调整窗口宽度计算
        if self.show_delete_button:  # 编辑模式
            base_width = min(screen_width / 3, max(screen_width / 4, 300))
        else:  # 显示模式
            base_width = min(screen_width / 6, max(screen_width / 8, 120))  # 显著减小显示模式的宽度
        
        # 根据课程数量和屏幕高度计算窗口高度
        # 每个课程项的基础高度
        item_height = screen_height / 20  # 基础高度为屏幕高度的 1/20
        
        # 计算所需总高度（包括边距和其他组件）
        total_height = (
            item_height * (len(self.courses) + 2)  # 课程数量 + 下拉框 + 添加按钮
            + 40  # 顶部边距
            + 40  # 底部边距
            + (len(self.courses) + 1) * 10  # 组件间距
        )
        
        # 确保窗口高度不超过屏幕高度的 80%
        max_height = screen_height * 0.8
        window_height = min(total_height, max_height)
        
        # 根据屏幕分辨率和显示模式调整最小尺寸
        if self.show_delete_button:  # 编辑模式
            if screen_height <= 768:  # 小屏幕
                min_width = 250
                min_height = 300
            elif screen_height <= 1080:  # 中等屏幕
                min_width = 300
                min_height = 400
            else:  # 大屏幕
                min_width = 350
                min_height = 500
        else:  # 显示模式
            if screen_height <= 768:  # 小屏幕
                min_width = 100
                min_height = 300
            elif screen_height <= 1080:  # 中等屏幕
                min_width = 120
                min_height = 400
            else:  # 大屏幕
                min_width = 140
                min_height = 500
        
        # 确保窗口尺寸不小于最小值
        window_width = max(base_width, min_width)
        window_height = max(window_height, min_height)
        
        return round(window_width), round(window_height)

    def check_delete_button_status(self):
        try:
            with open('change.txt', 'r', encoding='utf-8') as file:
                content = file.read().strip()
                return content == "1"
        except FileNotFoundError:
            return True  # 如果文件不存在，默认显示删除按钮
        except Exception as e:
            print(f"读取change.txt时发生错误: {e}")
            return True  # 发生错误时默认显示删除按钮

    def initUI(self):
        self.setWindowTitle('桌面课表软件')
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.CustomizeWindowHint | Qt.Tool)
        
        # 计算并设置窗口大小
        window_width, window_height = self.calculateWindowSize()
        self.setFixedSize(window_width, window_height)
        
        # 创建垂直布局
        layout = QVBoxLayout()
        
        # 设置布局的边距和间距
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 设置窗口的布局
        self.setLayout(layout)
        
        # 创建星期选择下拉框
        self.weekday_combo = QComboBox()
        self.weekday_combo.addItems(['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
        self.weekday_combo.setCurrentIndex(self.today_weekday - 1)
        self.weekday_combo.currentIndexChanged.connect(self.onWeekdayChanged)
        layout.addWidget(self.weekday_combo)

        # 创建添加课程按钮
        self.add_button = QPushButton('添加课程')
        self.add_button.clicked.connect(self.addCourse)
        
        # 根据 show_delete_button 状态设置添加按钮的可见性
        self.add_button.setVisible(self.show_delete_button)
        
        # 刷新课程组件显示
        self.refreshCourseWidgets()
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCourseList)
        self.timer.start(1000)

    def loadCoursesFromFile(self, weekday):
        try:
            with open('courses.json', 'r', encoding='utf-8') as file:
                courses_data = json.load(file)
                return courses_data.get(str(weekday), [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            print(f"JSON解码错误: {e}")
            return []

    def saveCoursesToFile(self):
        try:
            # 加载现有的课程数据
            try:
                with open('courses.json', 'r', encoding='utf-8') as file:
                    courses_data = json.load(file)
            except FileNotFoundError:
                courses_data = {}
            
            # 更新当前显示星期的课程数据
            courses_data[str(self.current_weekday)] = self.courses
            
            # 保存更新后的数据
            with open('courses.json', 'w', encoding='utf-8') as file:
                json.dump(courses_data, file, ensure_ascii=False, indent=4)
            
        except Exception as e:
            print(f"保存课程数据时发生错误: {e}")

    def refreshCourseWidgets(self):
        # 清除现有的组件
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        # 重新添加星期选择下拉框
        self.layout().addWidget(self.weekday_combo)

        # 获取当前课程总数
        total_courses = len(self.courses)

        # 添加课程组件
        for course in self.courses:
            course_widget = CourseWidget(course, self.show_delete_button, total_courses)
            self.layout().addWidget(course_widget)

        # 重新添加按钮
        self.layout().addWidget(self.add_button)

    def onWeekdayChanged(self, index):
        # 更新当前显示的星期
        self.current_weekday = index + 1
        # 加载选中星期的课程
        self.courses = self.loadCoursesFromFile(self.current_weekday)
        # 刷新显示
        self.refreshCourseWidgets()

    def removeCourse(self, course):
        if course in self.courses:
            self.courses.remove(course)
            self.saveCoursesToFile()
            self.refreshCourseWidgets()

    def addCourse(self):
        # 预定义课程列表
        subjects = ['语文', '数学', '英语', '信息', '美术', '音乐', '体育', '物理', '化学', '生物', '地理', '历史', '政治']
        
        # 创建课程选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('添加课程')
        dialog_layout = QVBoxLayout()
        
        # 课程选择下拉框
        subject_combo = QComboBox()
        subject_combo.addItems(subjects)
        dialog_layout.addWidget(QLabel('选择课程:'))
        dialog_layout.addWidget(subject_combo)
        
        # 时间选择下拉框
        time_combo = QComboBox()
        times = ['08:00-09:00', '09:10-10:10', '10:30-11:30', '13:00-14:00', 
                 '14:10-15:10', '15:30-16:30', '16:40-17:40']
        time_combo.addItems(times)
        dialog_layout.addWidget(QLabel('选择时间:'))
        dialog_layout.addWidget(time_combo)
        
        # 课程位置选择下拉框
        position_combo = QComboBox()
        positions = [str(i) for i in range(1, len(self.courses) + 2)]
        position_combo.addItems(positions)
        dialog_layout.addWidget(QLabel('选择位置:'))
        dialog_layout.addWidget(position_combo)
        
        # 确认和取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        dialog.setLayout(dialog_layout)
        
        # 显示对话框并等待用户响应
        if dialog.exec_() == QDialog.Accepted:
            course_name = subject_combo.currentText()
            course_time = time_combo.currentText()
            course_position = int(position_combo.currentText())
            
            new_course = {
                'name': course_name,
                'time': course_time,
                'position': course_position
            }
            
            # 更新当前显示星期的课程
            self.courses.insert(course_position - 1, new_course)
            self.saveCoursesToFile()
            self.refreshCourseWidgets()

    def updateCourseList(self):
        current_time = QTime.currentTime()
        # 只在显示当天课表时更新高亮
        if self.current_weekday == self.today_weekday:
            file_courses = self.loadCoursesFromFile(self.today_weekday)

            for i, course in enumerate(self.courses):
                course_time_range = course['time'].split('-')
                if len(course_time_range) != 2:
                    continue
                    
                start_time = QTime.fromString(course_time_range[0], 'hh:mm')
                end_time = QTime.fromString(course_time_range[1], 'hh:mm')
                course_widget = self.layout().itemAt(i + 1).widget()  # +1 是因为有下拉框

                if course_widget is None or not isinstance(course_widget, CourseWidget):
                    course_widget = CourseWidget(course, self.show_delete_button)
                    self.layout().insertWidget(i + 1, course_widget)

                # 检查当前时间是否在课程时间范围内
                if start_time <= current_time < end_time:
                    course_widget.name_label.setStyleSheet('background-color: yellow;')
                else:
                    course_widget.name_label.setStyleSheet('')

                if course not in file_courses:
                    self.courses.remove(course)
                    self.saveCoursesToFile()
                    self.layout().removeWidget(course_widget)
                    course_widget.setParent(None)
                    print(f"课程 {course} 已被移除。")

    def moveToRightTop(self):
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口尺寸
        size = self.geometry()
        # 计算右上角位置（留出一些边距）
        x = screen.width() - size.width() - 10  # 距离右边缘10像素
        y = 10  # 距离上边缘10像素
        # 移动窗口
        self.move(x, y)

    def editCourse(self, course):
        # 预定义课程列表
        subjects = ['语文', '数学', '英语', '信息', '美术', '音乐', '体育', '物理', '化学', '生物', '地理', '历史', '政治']
        
        # 创建课程编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('修改课程')
        dialog_layout = QVBoxLayout()
        
        # 课程选择下拉框
        subject_combo = QComboBox()
        subject_combo.addItems(subjects)
        subject_combo.setCurrentText(course['name'])  # 设置当前课程名称
        dialog_layout.addWidget(QLabel('选择课程:'))
        dialog_layout.addWidget(subject_combo)
        
        # 时间选择下拉框
        time_combo = QComboBox()
        times = ['08:00-09:00', '09:10-10:10', '10:30-11:30', '13:00-14:00', 
                 '14:10-15:10', '15:30-16:30', '16:40-17:40']
        time_combo.addItems(times)
        time_combo.setCurrentText(course['time'])  # 设置当前时间
        dialog_layout.addWidget(QLabel('选择时间:'))
        dialog_layout.addWidget(time_combo)
        
        # 课程位置选择下拉框
        position_combo = QComboBox()
        positions = [str(i) for i in range(1, len(self.courses) + 1)]
        position_combo.addItems(positions)
        current_position = self.courses.index(course) + 1
        position_combo.setCurrentText(str(current_position))  # 设置当前位置
        dialog_layout.addWidget(QLabel('选择位置:'))
        dialog_layout.addWidget(position_combo)
        
        # 确认和取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        dialog.setLayout(dialog_layout)
        
        # 显示对话框并等待用户响应
        if dialog.exec_() == QDialog.Accepted:
            # 从课程列表中移除原课程
            self.courses.remove(course)
            
            # 创建新的课程数据
            updated_course = {
                'name': subject_combo.currentText(),
                'time': time_combo.currentText(),
                'position': int(position_combo.currentText())
            }
            
            # 在新位置插入更新后的课程
            self.courses.insert(int(position_combo.currentText()) - 1, updated_course)
            
            # 保存并刷新显示
            self.saveCoursesToFile()
            self.refreshCourseWidgets()

    def setup_autostart(self):
        try:
            import os
            import sys
            
            # 检查是否是打包后的环境
            if not getattr(sys, 'frozen', False):
                print("开发环境，跳过自启动设置")
                return
            
            # 获取程序路径
            app_path = sys.executable
            app_dir = os.path.dirname(app_path)
            
            # 创建bat文件内容（添加cd命令切换目录）
            bat_content = f'''@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~0"" h",0)(window.close)&&exit
:begin
cd /d "{app_dir}"
"{app_path}"
'''
            
            # 保存bat文件
            bat_path = os.path.join(app_dir, 'course_startup.bat')
            try:
                with open(bat_path, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
                print(f"启动脚本已创建: {bat_path}")
                
                # 获取启动文件夹路径
                startup_folder = os.path.join(os.getenv('APPDATA'), 
                                            r'Microsoft\Windows\Start Menu\Programs\Startup')
                
                # 复制bat文件到启动文件夹
                startup_bat = os.path.join(startup_folder, 'Course.bat')
                import shutil
                shutil.copy2(bat_path, startup_bat)
                print(f"已复制启动脚本到启动文件夹: {startup_bat}")
                
            except Exception as e:
                print(f"创建或复制启动脚本失败: {e}")
                
        except Exception as e:
            print(f"设置开机自启动时发生错误: {e}")

    def check_and_fix_autostart(self):
        try:
            import winreg as reg
            import os
            import sys
            
            # 检查是否是打包后的环境
            if not getattr(sys, 'frozen', False):
                print("开发环境，跳过自启动检查")
                return
            
            # 获取程序路径
            app_path = sys.executable
            app_dir = os.path.dirname(app_path)
            script_path = os.path.join(app_dir, 'course_startup.py')
            pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            startup_cmd = f'"{pythonw_path}" "{script_path}"'
            
            try:
                # 检查注册表项
                key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, reg.KEY_READ)
                current_value, _ = reg.QueryValueEx(key, "CourseSchedule")
                reg.CloseKey(key)
                
                print(f"当前注册表值: {current_value}")
                print(f"期望的启动命令: {startup_cmd}")
                
                # 如果注册表项不正确，重新设置
                if current_value != startup_cmd:
                    print("注册表项不正确，正在修复...")
                    key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                                    r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                    0, reg.KEY_SET_VALUE)
                    reg.SetValueEx(key, "CourseSchedule", 0, reg.REG_SZ, startup_cmd)
                    reg.CloseKey(key)
                    print("注册表项已修复")
                    
            except WindowsError as e:
                # 如果注册表项不存在，创建它
                print("注册表项不存在，正在创建...")
                key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, reg.KEY_SET_VALUE)
                reg.SetValueEx(key, "CourseSchedule", 0, reg.REG_SZ, startup_cmd)
                reg.CloseKey(key)
                print("注册表项已创建")
                
            # 检查启动脚本是否存在
            if not os.path.exists(script_path):
                print("启动脚本不存在，正在创建...")
                self.setup_autostart()
            else:
                print("启动脚本已存在")
                
        except Exception as e:
            print(f"检查自启动设置时发生错误: {e}")

