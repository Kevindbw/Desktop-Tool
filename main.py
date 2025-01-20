import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer, QTime, Qt

class CourseWidget(QWidget):
    def __init__(self, course):
        super().__init__()
        self.course = course
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # 创建课程名称标签
        self.name_label = QLabel(self.course['name'])
        layout.addWidget(self.name_label)

        # 创建课程时间标签
        self.time_label = QLabel(self.course['time'])
        layout.addWidget(self.time_label)

        # 创建课程位置标签，将位置转换为字符串
        self.position_label = QLabel(str(self.course['position']))
        layout.addWidget(self.position_label)

        # 创建删除按钮
        self.delete_button = QPushButton('删除')
        self.delete_button.clicked.connect(self.deleteCourse)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def deleteCourse(self):
        # 从父窗口的课程列表中移除当前课程
        self.parent().removeCourse(self.course)

class CourseScheduleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('桌面课表软件')
        layout = QVBoxLayout()

        self.courses = self.loadCoursesFromFile()

        # 创建课程组件并添加到布局中
        self.refreshCourseWidgets()

        self.add_button = QPushButton('添加课程')
        self.add_button.clicked.connect(self.addCourse)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

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
        # 清空现有课程组件
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)
    
        # 重新添加所有课程组件
        for course in self.courses:
            course_widget = CourseWidget(course)
            self.layout().addWidget(course_widget)

        # 重新添加添加课程按钮
        self.layout().addWidget(self.add_button)

    def removeCourse(self, course):
        # 从课程列表中移除指定课程
        if course in self.courses:
            self.courses.remove(course)
            self.saveCoursesToFile()

            # 移除课程组件
            for i in range(self.layout().count()):
                course_widget = self.layout().itemAt(i).widget()
                if isinstance(course_widget, CourseWidget) and course_widget.course == course:
                    self.layout().removeWidget(course_widget)
                    course_widget.setParent(None)
                    break
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

        # 在指定位置插入新的课程
        new_course = {'name': course_name, 'time': course_time, 'position': course_position}
        self.courses.insert(course_position - 1, new_course)
        self.saveCoursesToFile()

        # 刷新课程组件
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


    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle('桌面课表软件')

        # 创建垂直布局
        layout = QVBoxLayout()

        # 从文件中读取课程数据
        self.courses = self.loadCoursesFromFile()

        # 创建课程组件并添加到布局中
        for course in self.courses:
            course_widget = CourseWidget(course)
            layout.addWidget(course_widget)

        # 创建添加课程按钮
        self.add_button = QPushButton('添加课程')
        self.add_button.clicked.connect(self.addCourse)
        layout.addWidget(self.add_button)

        # 设置窗口布局
        self.setLayout(layout)

        # 创建定时器，每秒更新一次课程列表
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

    def removeCourse(self, course):
        # 检查课程是否存在于列表中
        if course in self.courses:
            # 从课程列表中移除指定课程
            self.courses.remove(course)
            self.saveCoursesToFile()

            # 移除对应的课程组件
            for i in range(self.layout().count()):
                course_widget = self.layout().itemAt(i).widget()
                if isinstance(course_widget, CourseWidget) and course_widget.course == course:
                    self.layout().removeWidget(course_widget)
                    course_widget.setParent(None)
                    break


    def addCourse(self):
        # 打开输入对话框，获取课程信息
        course_name, ok = QInputDialog.getText(self, '添加课程', '请输入课程名称:')
        if not ok:
            return
    
        course_time, ok = QInputDialog.getText(self, '添加课程', '请输入课程时间:')
        if not ok:
            return
    
        course_position, ok = QInputDialog.getText(self, '添加课程', '请输入课程位置:')
        if not ok:
            return
    
        # 验证课程位置是否有效
        if not course_position.isdigit():
            QMessageBox.warning(self, '错误', '课程位置必须是数字')
            return
    
        course_position = int(course_position)
        if course_position < 1 or course_position > len(self.courses) + 1:
            QMessageBox.warning(self, '错误', '课程位置无效')
            return
    
        # 在指定位置插入新的课程
        new_course = {'name': course_name, 'time': course_time, 'position': course_position}
        self.courses.insert(course_position - 1, new_course)
        self.saveCoursesToFile()
    
        # 清空布局
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)
    
        # 重新添加所有课程组件
        for course in self.courses:
            course_widget = CourseWidget(course)
            self.layout().addWidget(course_widget)
        # 重新添加添加课程按钮
        self.layout().addWidget(self.add_button)
    def updateCourseList(self):
        # 获取当前时间
        current_time = QTime.currentTime()

        # 从文件中重新加载课程数据
        file_courses = self.loadCoursesFromFile()

        # 遍历程序缓存中的课程数据
        for i, course in enumerate(self.courses):
            course_time = QTime.fromString(course['time'].split('-')[0], 'hh:mm')
            course_widget = self.layout().itemAt(i).widget()

            # 如果课程组件不存在，创建一个新的
            if course_widget is None or not isinstance(course_widget, CourseWidget):
                course_widget = CourseWidget(course)
                self.layout().insertWidget(i, course_widget)

            # 根据当前时间高亮显示正在进行的课程
            if course_time <= current_time < course_time.addSecs(60 * 90):
                course_widget.name_label.setStyleSheet('background-color: yellow;')
            else:
                course_widget.name_label.setStyleSheet('')

            # 检查课程是否存在于文件中
            if course not in file_courses:
                # 从程序缓存中移除课程
                self.courses.remove(course)
                self.saveCoursesToFile()
                # 移除课程组件
                self.layout().removeWidget(course_widget)
                course_widget.setParent(None)
                print(f"课程 {course} 已被移除。")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CourseScheduleApp()
    ex.show()
    sys.exit(app.exec_())
