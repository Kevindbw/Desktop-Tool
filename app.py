import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox, QComboBox
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from course_widget import CourseWidget  # 导入CourseWidget

class CourseScheduleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.show_delete_button = self.check_delete_button_status()  # 确保在 initUI 之前初始化
        self.initUI()

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
        self.setWindowFlags(Qt.WindowStaysOnBottomHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        # 创建垂直布局
        layout = QVBoxLayout()

        # 设置窗口的布局
        self.setLayout(layout)

        # 获取今天的星期数 (1 - 星期一, 7 - 星期日)
        self.today_weekday = QDate.currentDate().dayOfWeek()
        print("今天：",self.today_weekday)

        # 创建星期选择下拉框
        self.weekday_combo = QComboBox()
        self.weekday_combo.addItems(['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
        self.weekday_combo.setCurrentIndex(self.today_weekday - 1)  # 设置当前星期
        self.weekday_combo.currentIndexChanged.connect(self.onWeekdayChanged)
        layout.addWidget(self.weekday_combo)

        # 从文件中读取课程数据
        self.courses = self.loadCoursesFromFile(self.today_weekday)
        self.current_weekday = self.today_weekday  # 记录当前显示的星期

        # 创建添加课程按钮
        self.add_button = QPushButton('添加课程')
        self.add_button.clicked.connect(self.addCourse)
        layout.addWidget(self.add_button)

        # 根据 show_delete_button 状态设置添加按钮的可见性
        self.add_button.setVisible(self.show_delete_button)

        # 在按钮创建之后再调用刷新方法
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
            with open('courses.json', 'r+', encoding='utf-8') as file:
                courses_data = json.load(file)
                # print("课表：",self.courses)
                # print("文件:",courses_data[str(self.today_weekday)])
                # 更新课程数据
                courses_data[str(self.today_weekday)] = self.courses
                # print("文件(问题):",courses_data)
                #重新保存整个文件
                file.seek(0)
                file.truncate()  # 清除文件中原来的内容
                json.dump(courses_data, file, ensure_ascii=False, indent=4)
                # exit(0)

        except FileNotFoundError:
            # 如果文件不存在，则创建新文件并保存
            courses_data = {str(self.today_weekday): self.courses}
            with open('courses.json', 'w', encoding='utf-8') as file:
                json.dump(courses_data, file, ensure_ascii=False, indent=4)

    def refreshCourseWidgets(self):
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        # 重新添加星期选择下拉框
        self.layout().addWidget(self.weekday_combo)

        for course in self.courses:
            course_widget = CourseWidget(course, self.show_delete_button)
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
            self.saveCoursesToFile()  # 删除课程后保存文件
            self.refreshCourseWidgets()

    def addCourse(self):
        course_name, ok = QInputDialog.getText(self, '添加课程', '请输入课程名称:')
        if not ok:
            return

        course_time, ok = QInputDialog.getText(self, '添加课程', '请输入课程时间 (格式: hh:mm-hh:mm):')
        if not ok:
            return

        # 检查时间格式是否正确
        if not self.isValidTimeFormat(course_time):
            QMessageBox.warning(self, '错误', '课程时间格式不正确，请使用 hh:mm-hh:mm 格式')
            return

        course_position, ok = QInputDialog.getText(self, '添加课程', '请输入课程位置:')
        if not ok:
            return

        if not course_position.isdigit():
            QMessageBox.warning(self, '错误', '课程位置必须是数字')
            return

        course_position = int(course_position)
        if course_position < 1 or course_position > len(self.courses) + 1:
            QMessageBox.warning(self, '错误', '课程位置无效')
            return

        new_course = {'name': course_name, 'time': course_time, 'position': course_position}
        self.courses.insert(course_position - 1, new_course)
        self.saveCoursesToFile()  # 添加课程后保存文件

        self.refreshCourseWidgets()

    def isValidTimeFormat(self, time_str):
        # 检查时间格式是否为 hh:mm-hh:mm
        parts = time_str.split('-')
        if len(parts) != 2:
            return False
        start_time = QTime.fromString(parts[0], 'hh:mm')
        end_time = QTime.fromString(parts[1], 'hh:mm')
        return start_time.isValid() and end_time.isValid()

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

