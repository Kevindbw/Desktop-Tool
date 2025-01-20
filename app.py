import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer, QTime, QDate
from course_widget import CourseWidget  # 导入CourseWidget

class CourseScheduleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('桌面课表软件')
        
        # 创建垂直布局
        layout = QVBoxLayout()

        # 设置窗口的布局
        self.setLayout(layout)

        # 获取今天的星期数 (1 - 星期一, 7 - 星期日)
        self.today_weekday = QDate.currentDate().dayOfWeek()
        print("今天：",self.today_weekday)
        # 从文件中读取课程数据
        self.courses = self.loadCoursesFromFile(self.today_weekday)

        # 创建添加课程按钮
        self.add_button = QPushButton('添加课程')
        self.add_button.clicked.connect(self.addCourse)
        layout.addWidget(self.add_button)

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
                return courses_data.get(str(weekday), [])  # 返回指定星期的课程列表
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

        for course in self.courses:
            course_widget = CourseWidget(course)
            self.layout().addWidget(course_widget)

        self.layout().addWidget(self.add_button)

    def removeCourse(self, course):
        if course in self.courses:
            self.courses.remove(course)
            self.saveCoursesToFile()  # 删除课程后保存文件
            self.refreshCourseWidgets()

    def addCourse(self):
        course_name, ok = QInputDialog.getText(self, '添加课程', '请输入课程名称:')
        if not ok:
            return

        course_time, ok = QInputDialog.getText(self, '添加课程', '请输入课程时间:')
        if not ok:
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

    def updateCourseList(self):
        current_time = QTime.currentTime()
        file_courses = self.loadCoursesFromFile(self.today_weekday)

        for i, course in enumerate(self.courses):
            course_time = QTime.fromString(course['time'].split('-')[0], 'hh:mm')
            course_widget = self.layout().itemAt(i).widget()

            if course_widget is None or not isinstance(course_widget, CourseWidget):
                course_widget = CourseWidget(course)
                self.layout().insertWidget(i, course_widget)

            if course_time <= current_time < course_time.addSecs(60 * 90):
                course_widget.name_label.setStyleSheet('background-color: yellow;')
            else:
                course_widget.name_label.setStyleSheet('')

            if course not in file_courses:
                self.courses.remove(course)
                self.saveCoursesToFile()
                self.layout().removeWidget(course_widget)
                course_widget.setParent(None)
                print(f"课程 {course} 已被移除。")
