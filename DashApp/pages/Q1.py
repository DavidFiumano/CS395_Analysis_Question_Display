import os.path as path 
import sys

PROJECT_ROOT = path.dirname(path.dirname(path.dirname(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
