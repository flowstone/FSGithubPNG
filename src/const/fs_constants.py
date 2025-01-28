from fs_base.const.app_constants import AppConstants


class FsConstants(AppConstants):
    """
    ---------------------
    宽度为0 高度为0,则表示窗口【宽高】由组件们决定
    ---------------------
    """
    # 主窗口相关常量
    APP_WINDOW_WIDTH = 300
    APP_WINDOW_HEIGHT = 300
    APP_WINDOW_TITLE = "FSGithubPNG"
    VERSION = "0.1.2"
    COPYRIGHT_INFO = f"© 2025 {APP_WINDOW_TITLE}"
    # 悬浮球相关常量
    APP_MINI_SIZE = 80
    APP_MINI_WINDOW_TITLE = ""

    # 工具栏相关常量
    TOOLBAR_HELP_TITLE = "帮助"
    TOOLBAR_README_TITLE = "说明"
    TOOLBAR_AUTHOR_TITLE = "作者"





    # 共用的常量，应用图标
    APP_ICON_FULL_PATH = "resources/images/app.ico"
    APP_MINI_ICON_FULL_PATH = "resources/images/app_mini.ico"
    APP_BAR_ICON_FULL_PATH = "resources/images/app_bar.ico"
    UPLOAD_IMAGE_FULL_PATH = "resources/images/upload.svg"
    PROJECT_ADDRESS = "https://github.com/flowstone/FSGithubPNG"
    BASE_QSS_PATH = "resources/qss/base.qss"
    LICENSE_FILE_PATH = "resources/txt/LICENSE"




    # 保存文件路径
    AppConstants.SAVE_FILE_PATH_WIN = "C:\\FSGithubPNG\\"
    AppConstants.SAVE_FILE_PATH_MAC = "~/FSGithubPNG/"
    EXTERNAL_APP_INI_FILE = "app.ini"

    APP_INI_FILE = "app.ini"
    HELP_PDF_FILE_PATH = "resources/pdf/help.pdf"
    FONT_FILE_PATH = "resources/fonts/AlimamaFangYuanTiVF-Thin.ttf"

    #首选项
    PREFERENCES_WINDOW_TITLE = "首选项"
    PREFERENCES_WINDOW_TITLE_ABOUT = "关于"
    PREFERENCES_WINDOW_TITLE_GENERAL = "常规"

    GITHUB_TOKEN_KEY = "github.token"
    GITHUB_REPO_KEY = "github.repo"
    GITHUB_ROOT_FOLDER_KEY = "github.root_folder"

    # 默认值
    NEW_CONFIG = {
        GITHUB_TOKEN_KEY: "",
        GITHUB_REPO_KEY: "",
        GITHUB_ROOT_FOLDER_KEY: "",
    }

    AppConstants.DEFAULT_CONFIG = {**AppConstants.DEFAULT_CONFIG, **NEW_CONFIG}
    # 类型映射
    NEW_CONFIG_TYPES = {
        GITHUB_TOKEN_KEY: str,
        GITHUB_REPO_KEY: str,
        GITHUB_ROOT_FOLDER_KEY: str,
    }
    AppConstants.CONFIG_TYPES = {**AppConstants.CONFIG_TYPES, **NEW_CONFIG_TYPES}
    ################### INI设置 #####################