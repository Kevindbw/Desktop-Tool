from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont

class CourseWidget(QWidget):
    def __init__(self, course, show_delete_button):
        super().__init__()
        self.course = course
        self.show_delete_button = show_delete_button
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # 课程名称的字体设置
        name_font = QFont()
        name_font.setPointSize(20)  # 较大的字号
        name_font.setBold(True)     # 粗体

        # 时间的字体设置
        time_font = QFont()
        time_font.setPointSize(10)  # 较小的字号
        time_font.setBold(False)    # 非粗体

        self.name_label = QLabel(self.course['name'])
        self.name_label.setFont(name_font)  # 应用课程名称字体
        layout.addWidget(self.name_label)

        self.time_label = QLabel(self.course['time'])
        self.time_label.setFont(time_font)  # 应用时间字体
        layout.addWidget(self.time_label)

        self.delete_button = QPushButton('删除')
        self.delete_button.clicked.connect(self.deleteCourse)
        layout.addWidget(self.delete_button)

        self.delete_button.setVisible(self.show_delete_button)

        self.setLayout(layout)

    def deleteCourse(self):
        reply = QMessageBox.question(self, '确认删除', f"确定要删除课程 '{self.course['name']}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent().removeCourse(self.course)
