import sys
from PyQt5.QtWidgets import QApplication
from course_widget import CourseWidget  # 导入CourseWidget
from app import CourseScheduleApp        # 导入CourseScheduleApp
import json

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CourseScheduleApp()
    ex.show()
    sys.exit(app.exec_())
