import sys
import os
import datetime
import socket

from fs_base.base_util import BaseUtil
from loguru import logger
from src.const.fs_constants import FsConstants


class CommonUtil(BaseUtil):




    # 获得外部目录
    @staticmethod
    def get_external_path() -> str:
        # 使用内置配置路径
        # SAVE_FILE_PATH_WIN = "C:\\FSGithubPNG\\"
        # SAVE_FILE_PATH_MAC = "~/FSGithubPNG/"
        return FsConstants.SAVE_FILE_PATH_WIN if CommonUtil.check_win_os() else CommonUtil.get_mac_user_path()