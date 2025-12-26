#!/usr/bin/env python3
"""
Simple folder picker dialog helper.
Used as a subprocess to avoid tkinter main thread issues in Flask.
"""
import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


def pick_folder(initial_dir=None):
    """Open folder picker and return selected path."""
    # Create hidden root window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Set initial directory
    try:
        if initial_dir and initial_dir != 'None' and Path(initial_dir).exists():
            initial = initial_dir
        else:
            initial = str(Path.home())
    except (TypeError, ValueError):
        initial = str(Path.home())

    # Open folder picker
    selected = filedialog.askdirectory(
        title='Wähle Speicherort für Memoir-Daten',
        initialdir=initial
    )

    # Clean up
    root.destroy()

    # Return selected path or empty string if cancelled
    if selected:
        return str(Path(selected).resolve())
    return ""


if __name__ == '__main__':
    # Get initial directory from command line argument
    initial_dir = sys.argv[1] if len(sys.argv) > 1 else None

    # Pick folder and print result
    result = pick_folder(initial_dir)
    print(result)
