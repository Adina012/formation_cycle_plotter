"""Main entry point for Formation Cycle Plotter application."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import with absolute path after adding to sys.path
from src import gui

if __name__ == "__main__":
    gui.main()
