import os
import sys

# Ensure src is in python path for relative imports to work from root execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kosdra.src.ui.app import render_app

if __name__ == "__main__":
    render_app()