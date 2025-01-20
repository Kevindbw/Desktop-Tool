from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

class CourseWidget(QWidget):
    def __init__(self, course):
        super().__init__()
        self.course = course
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        self.name_label = QLabel(self.course['name'])
        layout.addWidget(self.name_label)

        self.time_label = QLabel(self.course['time'])
        layout.addWidget(self.time_label)

        self.position_label = QLabel(str(self.course['position']))
        layout.addWidget(self.position_label)

        self.delete_button = QPushButton('删除')
        self.delete_button.clicked.connect(self.deleteCourse)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def deleteCourse(self):
        self.parent().removeCourse(self.course)
