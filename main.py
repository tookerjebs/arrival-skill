"""
Main entry point for the Skill Reroll Automation tool.
"""

import tkinter as tk
from ui import SkillRerollUI

class SkillRerollApp:
    def __init__(self):
        """Initialize the application"""
        self.root = tk.Tk()
        self.ui = SkillRerollUI(self.root)

        # Set up cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Clean up resources when the window is closed"""
        self.ui.on_closing()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SkillRerollApp()
    app.run()
