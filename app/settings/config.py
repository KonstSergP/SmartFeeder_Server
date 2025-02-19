import logging
import sys
from dynaconf import Dynaconf


settings = Dynaconf(
    settings_files=["./app/settings/settings.toml"]
)


log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(settings.log_format))
log.addHandler(handler)
log.setLevel(settings.log_level)
