import logging
import sys
from os.path import join
from dynaconf import Dynaconf


settings = Dynaconf(
    settings_files=[join("app", "settings", "settings.toml")]
)


log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(handler)
log.setLevel(settings.log_level)
