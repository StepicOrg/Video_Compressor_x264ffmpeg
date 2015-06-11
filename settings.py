import os
URL_GET_FILE_PATH = "get"
MAX_WORKERS = 4
FFPROBE_RUN_PATH = "ffprobe"
DEFAULT_OUT_FILE_SIZE_BYTES = 190 * 1024 * 1024


PACKAGE_ROOT = os.path.dirname(os.path.realpath(__file__))
__UPLOADS__ = os.path.join(PACKAGE_ROOT, "video", "uploads")
__COMPRESSED_FILES_FOLDER__ = os.path.join(PACKAGE_ROOT, "video", "converted")
__STATIC__ = os.path.join(os.path.dirname(__file__), "static")