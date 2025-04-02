import logging
import sys
from os.path import join
from dynaconf import Dynaconf


settings = Dynaconf(
    settings_files=[join("app", "settings", "settings.toml")]
)


log = logging.getLogger(__name__)
log.setLevel(settings.log_level)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(handler)

file_handler = logging.FileHandler(settings.log_file)
file_handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(file_handler)
