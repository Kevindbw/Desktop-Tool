from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CourseWidget(QWidget):
    def __init__(self, course, show_delete_button, total_courses):
        super().__init__()
        self.course = course
        self.show_delete_button = show_delete_button  # 这个值现在来自 change.txt
        self.total_courses = total_courses
        self.initUI()

    def calculateFontSize(self):
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        screen_height = screen.height()
        screen_width = screen.width()

        # 计算基础字体大小
        # 考虑屏幕高度、宽度和课程数量
        base_size = min(screen_height / (self.total_courses * 3), screen_width / 50)
        
        # 根据不同的屏幕分辨率范围调整字体大小
        if screen_height <= 768:  # 小屏幕
            name_size = max(12, min(base_size * 0.8, 18))
            time_size = max(8, min(base_size * 0.4, 12))
        elif screen_height <= 1080:  # 中等屏幕
            name_size = max(16, min(base_size * 0.9, 24))
            time_size = max(10, min(base_size * 0.5, 14))
        else:  # 大屏幕
            name_size = max(20, min(base_size, 32))
            time_size = max(12, min(base_size * 0.6, 16))

        # 根据课程数量进行微调
        if self.total_courses > 7:
            name_size *= 0.85
            time_size *= 0.85
        elif self.total_courses < 4:
            name_size *= 1.2
            time_size *= 1.2

        return round(name_size), round(time_size)

    def initUI(self):
        layout = QHBoxLayout()

        # 计算字体大小
        name_size, time_size = self.calculateFontSize()

        # 课程名称的字体设置
        name_font = QFont()
        name_font.setPointSize(name_size)
        name_font.setBold(True)

        # 时间的字体设置
        time_font = QFont()
        time_font.setPointSize(time_size)
        time_font.setBold(False)

        # 创建并设置课程名称标签
        self.name_label = QLabel(self.course['name'])
        self.name_label.setFont(name_font)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        # 创建并设置时间标签
        self.time_label = QLabel(self.course['time'])
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        # 根据 show_delete_button 控制时间标签的显示
        self.time_label.setVisible(self.show_delete_button)

        # 添加修改按钮
        self.edit_button = QPushButton('修改')
        self.edit_button.clicked.connect(self.editCourse)
        self.edit_button.setMinimumWidth(40)
        layout.addWidget(self.edit_button)

        # 添加删除按钮
        self.delete_button = QPushButton('删除')
        self.delete_button.clicked.connect(self.deleteCourse)
        self.delete_button.setMinimumWidth(40)
        layout.addWidget(self.delete_button)

        # 设置按钮可见性
        self.delete_button.setVisible(self.show_delete_button)
        self.edit_button.setVisible(self.show_delete_button)

        # 设置布局的间距
        layout.setSpacing(10)
        layout.setContentsMargins(10, 5, 10, 5)

        self.setLayout(layout)

    def editCourse(self):
        self.parent().editCourse(self.course)

    def deleteCourse(self):
        reply = QMessageBox.question(self, '确认删除', 
                                   f"确定要删除课程 '{self.course['name']}' 吗？",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent().removeCourse(self.course)
