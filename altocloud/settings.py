import os

from utils import Logger

logger = Logger.get_logger("debug")

project_home_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(project_home_dir, "config.yml")
logger.debug(f"using the config {config_file}")
