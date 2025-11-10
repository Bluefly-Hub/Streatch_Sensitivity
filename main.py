"""
Main entry point for the Well Automation Application
Run this file to start the GUI
"""
import tkinter as tk
from GUI_Automation import AutomationGUI


def main():
    """Start the automation GUI application"""
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
