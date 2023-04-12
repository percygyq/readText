#!/user/bin/env python3
# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Selector & Drag and Drop")
        self.setGeometry(200, 200, 300, 200)

        select_file_button = QtWidgets.QPushButton("Select File", self)
        select_file_button.setGeometry(50, 30, 200, 50)
        select_file_button.clicked.connect(self.select_file)

        self.file_path_input = QtWidgets.QLineEdit(self)
        self.file_path_input.setGeometry(50, 90, 200, 30)

        # 启用拖放功能
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # 判断进入窗口的数据是否可接受
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if url.toString().endswith('.txt') or url.toString().startsWith('image/'):
                        event.accept()
                        self.update()
                        return
        event.ignore()

    def dropEvent(self, event):
        # 处理拖放事件
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.file_path_input.setText(url.toLocalFile())
                return

    def select_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setDirectory('/path/to/default/directory')
        file_dialog.setNameFilter('Text files (*.txt)')

        if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            self.file_path_input.setText(selected_file)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
