import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer, QTime
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

        # 从文件中读取课程数据
        self.courses = self.loadCoursesFromFile()

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


    def loadCoursesFromFile(self):
        try:
            with open('courses.json', 'r', encoding='utf-8') as file:
                courses = json.load(file)
                for course in courses:
                    if 'position' not in course:
                        course['position'] = len(courses) + 1
                return courses
        except FileNotFoundError:
            return []

    def saveCoursesToFile(self):
        with open('courses.json', 'w', encoding='utf-8') as file:
            json.dump(self.courses, file)

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
            self.saveCoursesToFile()
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
        self.saveCoursesToFile()

        self.refreshCourseWidgets()

    def updateCourseList(self):
        current_time = QTime.currentTime()
        file_courses = self.loadCoursesFromFile()

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
