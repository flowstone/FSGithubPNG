import sys
import requests
import base64
import datetime
import uuid
import tempfile
import os
from PySide6.QtGui import QShortcut, QKeySequence, QImage
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QFileDialog, QTextEdit, QInputDialog, QWidget, QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from fs_base.config_manager import ConfigManager
from fs_base.widget import CustomProgressBar

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from loguru import logger


class UploadThread(QThread):
    upload_finished = Signal(str)  # 信号用于通知上传结果

    def __init__(self, file_path, github_token, github_repo, github_root_folder,
                 github_cdn_checked=False,github_markdown_checked=False, is_temp_file=False):
        super().__init__()
        self.file_path = file_path
        self.github_token = github_token
        self.github_repo = github_repo
        self.github_root_folder = github_root_folder
        self.github_cdn_checked = github_cdn_checked
        self.github_markdown_checked = github_markdown_checked
        self.is_temp_file = is_temp_file  # 新增参数


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
            unique_name = f"{CommonUtil.get_current_time_str()}.{extension}"
            base_folder = self.github_root_folder
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
                if self.github_cdn_checked:
                    image_url = download_url.replace("https://raw.githubusercontent.com/",
                                                   "https://cdn.jsdelivr.net/gh/").replace(f"{self.github_repo}/",
                                                                                           f"{self.github_repo}@")
                    logger.info(f"CDN 加速jsDelivr：{image_url}")
                else:
                    image_url = download_url
                    logger.info(f"上传成功！图片外链：{image_url}")

                if self.github_markdown_checked:
                    image_url = f"![{unique_name}]({image_url})"
                    logger.info(f"上传成功！图片外链,Markdown 语法：{image_url}")

                self.upload_finished.emit(f"上传成功！图片外链：\n{image_url}")


            else:
                logger.warning(f"上传失败！{response.json().get('message')}")
                self.upload_finished.emit(f"上传失败！\n{response.json().get('message')}")
        except Exception as e:
            logger.error(f"发生错误：{str(e)}")
            self.upload_finished.emit(f"发生错误：\n{str(e)}")
        finally:
            # 如果是临时文件则删除
            if self.is_temp_file:
                try:
                    os.remove(self.file_path)
                except Exception as e:
                    logger.error(f"删除临时文件失败: {str(e)}")

class GitHubImageUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub 图床")
        self.setGeometry(300, 200, 600, 400)
        self.config_manager = ConfigManager()
        self.config_manager.config_updated.connect(self.on_config_updated)
        # 初始化 GitHub 配置
        self.github_token = self.config_manager.get_config(FsConstants.GITHUB_TOKEN_KEY)
        self.github_repo = self.config_manager.get_config(FsConstants.GITHUB_REPO_KEY)
        self.github_root_folder = self.config_manager.get_config(FsConstants.GITHUB_ROOT_FOLDER_KEY)
        self.github_cdn_checked = self.config_manager.get_config(FsConstants.GITHUB_CDN_CHECKED_KEY)
        self.github_markdown_checked = self.config_manager.get_config(FsConstants.GITHUB_MARKDOWN_CHECKED_KEY)

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
        remark_label = QLabel("🧚‍♀️ 新增剪贴板图片上传，使用右键或Ctrl+V", self)
        remark_label.setStyleSheet("color: gray;")

        self.layout.addWidget(self.result_label)
        self.layout.addWidget(remark_label)

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
        # 添加快捷键 Ctrl+V 用于粘贴剪贴板图片
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.upload_from_clipboard)

    def upload_from_clipboard(self):
        """从剪贴板上传图片"""
        try:
            clipboard = QApplication.clipboard()
            image = clipboard.image()

            if not image.isNull():
                try:
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(
                            suffix=".png", delete=False
                    ) as temp_file:
                        temp_path = temp_file.name

                    # 保存图片到临时文件
                    image.save(temp_path, "PNG")
                    logger.info(f"已从剪贴板保存临时文件: {temp_path}")

                    # 启动上传线程并标记为临时文件
                    self.upload_image(temp_path, is_temp_file=True)

                except Exception as e:
                    logger.error(f"保存剪贴板图片失败: {str(e)}")
                    self.result_display.setText(f"错误: {str(e)}")
            else:
                self.result_display.setText("剪贴板中没有检测到图片！")
                logger.warning("剪贴板内容不是图片")
        except Exception as e:
            logger.error(f"从剪贴板读取图片失败: {str(e)}")
            self.result_display.setText(f"错误: {str(e)}")
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        paste_action = menu.addAction("粘贴剪贴板图片")
        paste_action.triggered.connect(self.upload_from_clipboard)
        menu.exec(event.globalPos())
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

    def upload_image(self, file_path, is_temp_file=False):
        """启动上传线程"""
        if not self.github_token or not self.github_repo:
            logger.info("请先在设置中配置 GitHub Token 和仓库信息！")
            self.result_display.setText("请先在设置中配置 GitHub Token 和仓库信息！")
            return

        # 显示正在上传
        self.result_display.setText("正在上传，请稍候...")
        logger.info("正在上传，请稍候...")
        self.progress_bar.set_range(0,0)
        # 创建并启动上传线程
        self.upload_thread = UploadThread(file_path, self.github_token, self.github_repo, self.github_root_folder,
                                          self.github_cdn_checked, self.github_markdown_checked, is_temp_file)
        self.upload_thread.upload_finished.connect(self.display_result)
        self.upload_thread.start()
        self.progress_bar.show()

    def display_result(self, result):
        """显示上传结果"""
        self.progress_bar.hide()
        self.result_display.setText(result)

    def on_config_updated(self, key, value):
        if key == FsConstants.GITHUB_TOKEN_KEY:
            self.github_token = value
        elif key == FsConstants.GITHUB_REPO_KEY:
            self.github_repo = value
        elif key == FsConstants.GITHUB_ROOT_FOLDER_KEY:
            self.github_root_folder = value


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitHubImageUploader()
    window.show()
    sys.exit(app.exec())
