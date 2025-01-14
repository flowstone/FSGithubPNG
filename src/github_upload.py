import sys
import requests
import base64
import datetime
import uuid
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QFileDialog, QTextEdit, QInputDialog, QWidget, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.util.config_util import ConfigUtil

from src.widget.custom_progress_widget import CustomProgressBar


class UploadThread(QThread):
    upload_finished = Signal(str)  # 信号用于通知上传结果

    def __init__(self, file_path, github_token, github_repo):
        super().__init__()
        self.file_path = file_path
        self.github_token = github_token
        self.github_repo = github_repo

    def run(self):
        """上传图片到 GitHub"""
        try:
            # 获取当前日期
            now = datetime.datetime.now()
            year = str(now.year)
            month = str(now.month).zfill(2)

            # 生成唯一文件名
            original_name = self.file_path.split("/")[-1]
            extension = original_name.split(".")[-1]
            unique_name = f"{uuid.uuid4().hex}.{extension}"
            base_folder = ConfigUtil.get_ini_github_base_folder()
            target_path =f"{base_folder}/{year}/{month}/{unique_name}" if base_folder else f"{year}/{month}/{unique_name}"

            # 上传图片到 GitHub
            url = f"https://api.github.com/repos/{self.github_repo}/contents/{target_path}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            with open(self.file_path, "rb") as file:
                content = file.read()

            data = {
                "message": f"上传图片 {original_name}",
                "content": base64.b64encode(content).decode("utf-8")
            }
            response = requests.put(url, json=data, headers=headers)

            if response.status_code == 201:
                download_url = response.json().get("content").get("download_url")
                self.upload_finished.emit(f"上传成功！图片外链：\n{download_url}")
            else:
                self.upload_finished.emit(f"上传失败！\n{response.json().get('message')}")
        except Exception as e:
            self.upload_finished.emit(f"发生错误：\n{str(e)}")


class GitHubImageUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub 图床")
        self.setGeometry(300, 200, 600, 400)

        # 初始化 GitHub 配置
        self.github_token = ConfigUtil.get_ini_github_token()
        self.github_repo = ConfigUtil.get_ini_github_repo()

        # 设置拖拽支持
        self.setAcceptDrops(True)

        # 主界面布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 上传结果显示
        self.result_label = QLabel("拖拽图片到窗口内，或双击选择图片上传", self)
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;  padding: 10px;")

        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.result_label)

        # 创建 QLabel
        upload_label = QLabel()
        upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 将图片设置为标签的内容
        upload_label.setPixmap(QPixmap(CommonUtil.get_resource_path(FsConstants.UPLOAD_IMAGE_FULL_PATH)))
        self.layout.addWidget(upload_label)

        # 添加垂直间距
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 添加进度条
        self.progress_bar = CustomProgressBar()
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.result_display)

        # 上传线程
        self.upload_thread = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """处理拖拽释放事件"""
        file_urls = event.mimeData().urls()
        if file_urls:
            file_path = file_urls[0].toLocalFile()
            self.upload_image(file_path)

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if file_path:
            self.upload_image(file_path)

    def upload_image(self, file_path):
        """启动上传线程"""
        if not self.github_token or not self.github_repo:
            self.result_display.setText("请先在设置中配置 GitHub Token 和仓库信息！")
            return

        # 显示正在上传
        self.result_display.setText("正在上传，请稍候...")
        self.progress_bar.set_range(0,0)
        # 创建并启动上传线程
        self.upload_thread = UploadThread(file_path, self.github_token, self.github_repo)
        self.upload_thread.upload_finished.connect(self.display_result)
        self.upload_thread.start()
        self.progress_bar.show()

    def display_result(self, result):
        """显示上传结果"""
        self.progress_bar.hide()
        self.result_display.setText(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitHubImageUploader()
    window.show()
    sys.exit(app.exec())
