import os

URL_GET_DIRECT_FILE_PATH = "get"
URL_GET_FILE_PAGE_PATH = "status"
MAX_WORKERS = 4
FFPROBE_RUN_PATH = "ffprobe"
DEFAULT_OUT_FILE_SIZE_BYTES = 190 * 1024 * 1024

PACKAGE_ROOT = os.path.dirname(os.path.realpath(__file__))
VIDEO_DIR = ("/video" if "IS_DOCKER" in os.environ else
             os.path.join(PACKAGE_ROOT, "video"))
__UPLOADS__ = os.path.join(VIDEO_DIR, "uploads")
__COMPRESSED_FILES_FOLDER__ = os.path.join(VIDEO_DIR, "converted")
__STATIC__ = os.path.join(os.path.dirname(__file__), "static")
