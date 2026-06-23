import os
import sys


BACKEND_SRC = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")
)
if BACKEND_SRC not in sys.path:
    sys.path.insert(0, BACKEND_SRC)
