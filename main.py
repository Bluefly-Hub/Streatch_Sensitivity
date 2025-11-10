"""
Main entry point for the Well Automation Application
Run this file to start the GUI
"""
import tkinter as tk
from GUI_Automation import AutomationGUI
from updater import check_and_update
from version import __version__


def main():
    """Start the automation GUI application"""
    # Check for updates first
    print(f"Well Automation v{__version__}")
    if check_and_update():
        # Update is being installed, exit the application
        return
    
    # Start the GUI
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
