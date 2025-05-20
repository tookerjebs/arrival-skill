"""
Game connector module for the Skill Reroll Automation tool.
Handles connecting to the game window and sending clicks.
"""

from pywinauto import Application
from tkinter import messagebox
import win32gui
import win32con

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

    def click_at_position(self, coords, adjust_for_client_area=True):
        """
        Click at the specified coordinates in the game window using standard click() method
        This method sends Windows messages directly without moving the mouse cursor

        Args:
            coords: Tuple of (x, y) coordinates relative to the window
            adjust_for_client_area: Whether to adjust coordinates for client area (title bar offset)
                                   Set to True if coords are relative to window including title bar
                                   Set to False if coords are already relative to client area
        """
        if not self.game_window:
            return False

        try:
            # If we need to adjust for client area (title bar and borders)
            if adjust_for_client_area:
                # Get the offset between window and client area
                offset = self.get_window_client_offset()

                if offset:
                    # Adjust the coordinates by subtracting the offset
                    # This converts window coordinates to client coordinates
                    adjusted_coords = (coords[0] - offset[0], coords[1] - offset[1])
                    self.game_window.click(coords=adjusted_coords)
                    return True

            # If no adjustment needed or offset couldn't be determined
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

    def get_client_rect(self):
        """
        Get the client rectangle of the game window.
        This is the area inside the window borders and title bar.
        """
        if not self.game_window:
            return None
        try:
            # Get the window handle
            hwnd = self.game_window.handle

            # Get client rectangle in client coordinates (0,0 is top-left of client area)
            client_rect = win32gui.GetClientRect(hwnd)

            # Convert client coordinates (0,0) to screen coordinates
            client_pos = win32gui.ClientToScreen(hwnd, (0, 0))

            # Return as (left, top, right, bottom) tuple
            return (
                client_pos[0],
                client_pos[1],
                client_pos[0] + client_rect[2],
                client_pos[1] + client_rect[3]
            )
        except Exception as e:
            self.update_status(f"Failed to get client rect: {str(e)}")
            return None

    def get_window_client_offset(self):
        """
        Calculate the offset between window coordinates and client coordinates.
        Returns (offset_x, offset_y) tuple or None if not available.
        """
        if not self.game_window:
            return None

        try:
            # Get window and client rectangles
            window_rect = self.get_window_rect()
            client_rect = self.get_client_rect()

            if not window_rect or not client_rect:
                return None

            # Calculate offsets
            offset_x = client_rect[0] - window_rect.left
            offset_y = client_rect[1] - window_rect.top

            return (offset_x, offset_y)
        except Exception as e:
            self.update_status(f"Failed to calculate window-client offset: {str(e)}")
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

    def convert_to_client_coords(self, window_x, window_y):
        """
        Convert window-relative coordinates to client-relative coordinates.
        This adjusts for the title bar and borders.
        """
        if not self.game_window:
            return (window_x, window_y, False)

        try:
            offset = self.get_window_client_offset()
            if not offset:
                return (window_x, window_y, False)

            client_x = window_x - offset[0]
            client_y = window_y - offset[1]
            return (client_x, client_y, True)
        except Exception:
            return (window_x, window_y, False)

    def is_connected(self):
        """Check if connected to game window"""
        return self.game_window is not None
