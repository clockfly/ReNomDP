"""constant data."""
import os
from settings import DATA_DIR_NAME, STORAGE_DIR_NAME

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, DATA_DIR_NAME)
STORAGE_DIR = os.path.join(BASE_DIR, STORAGE_DIR_NAME)

INTERPOLATE_ITEMS = ['none', 'linear', 'spline', 'nearest_index']
