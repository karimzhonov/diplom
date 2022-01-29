import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = os.path.join(BASE_DIR, 'dataset')
