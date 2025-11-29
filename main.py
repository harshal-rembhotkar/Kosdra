import os
import sys

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import render_app

if __name__ == "__main__":
    render_app()
