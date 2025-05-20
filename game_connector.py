"""
Game connector module for the Skill Reroll Automation tool.
Handles connecting to the game window and sending clicks.
"""

from pywinauto import Application
from tkinter import messagebox

class GameConnector:
    def __init__(self, status_callback=None):
        """
        Initialize the game connector
        """
        self.game_window = None
        self.status_callback = status_callback

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def connect_to_game(self):
        """
        Connect to the game window by class name (most reliable method)
        Returns: bool: True if connection successful, False otherwise
        """
        try:
            app = Application()
            app.connect(class_name="D3D Window")

            # Get all D3D Windows and find the one that's likely the game
            windows = app.windows(class_name="D3D Window")

            # If there's only one D3D Window, use it
            if len(windows) == 1:
                self.game_window = windows[0]
            # If there are multiple, try to find the right one
            elif len(windows) > 1:
                # First try to find one with "Cabal" in the title
                for window in windows:
                    if "Cabal" in window.window_text():
                        self.game_window = window
                        break
                # If that fails, use the first visible one
                else:
                    for window in windows:
                        if window.is_visible():
                            self.game_window = window
                            break
                    # If all else fails, use the first one
                    else:
                        self.game_window = windows[0]
            else:
                raise Exception("No D3D Window found")

            # Verify connection
            if self.game_window.is_visible() and self.game_window.is_enabled():
                return True
            else:
                raise Exception("Found window but it's not visible or enabled")

        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to the game. Make sure it's running.\nError: {str(e)}")
            return False

    def click_at_position(self, coords):
        """
        Click at the specified coordinates in the game window using standard click() method
        This method sends Windows messages directly without moving the mouse cursor
        """
        if not self.game_window:
            return False

        try:
            # Use the standard click method (not click_input)
            # This sends Windows messages directly without moving the mouse cursor
            self.game_window.click(coords=coords)
            return True
        except Exception as e:
            self.update_status(f"Click failed: {str(e)}")
            return False

    def get_window_rect(self):
        """Get the rectangle of the game window"""
        if not self.game_window:
            return None
        try:
            return self.game_window.rectangle()
        except Exception:
            return None

    def convert_to_window_coords(self, screen_x, screen_y):
        """Convert screen coordinates to window-relative coordinates"""
        if not self.game_window:
            return (screen_x, screen_y, False)

        try:
            rect = self.game_window.rectangle()
            rel_x = screen_x - rect.left
            rel_y = screen_y - rect.top
            return (rel_x, rel_y, True)
        except Exception:
            return (screen_x, screen_y, False)

    def is_connected(self):
        """Check if connected to game window"""
        return self.game_window is not None
