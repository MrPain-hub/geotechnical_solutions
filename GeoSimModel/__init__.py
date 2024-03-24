import os

from . import create_models
from . import solve
from . import visualization

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

path_data = os.path.dirname(current_file_path) + "/data/"
