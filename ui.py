"""
UI module for the Skill Reroll Automation tool.
Simplified version with single offensive and defensive stat fields.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import mouse
import threading
import re
import stats_data
from game_connector import GameConnector
from automation import SkillRerollAutomator

class SkillRerollUI:
    def __init__(self, root):
        """Initialize the UI"""
        self.root = root
        self.root.title("Skill Reroll Automation")
        self.root.resizable(True, True)
        self.root.minsize(400, 500)  # Set minimum window size

        # Variables
        self.apply_button_coords = None
        self.change_button_coords = None
        self.detection_region = None
        self.apply_coord_var = None
        self.change_coord_var = None
        self.detection_region_var = None
        self.status_var = None
        self.running = False

        # Create game connector and automator
        self.game_connector = GameConnector(self.update_status)
        self.automator = SkillRerollAutomator(self.game_connector, self.update_status)

        # Set up kill switch (Escape key)
        self.setup_kill_switch()

        # Create UI
        self.create_ui()

    def update_status(self, message):
        """Update the status display and log"""
        # Update the status label with the current message
        if hasattr(self, 'status_var') and self.status_var:
            self.status_var.set(message)

        # Add the message to the log with timestamp
        if hasattr(self, 'log_text'):
            # Get current time
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Format the log entry
            log_entry = f"[{timestamp}] {message}\n"

            # Enable editing, insert text, then disable again
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)  # Auto-scroll to the end
            self.log_text.config(state=tk.DISABLED)

    def setup_kill_switch(self):
        """Set up a global hotkey (ESC) to stop the automation"""
        # Register the ESC key as a kill switch
        keyboard.add_hotkey('esc', self.emergency_stop)

    def emergency_stop(self):
        """Emergency stop function triggered by the kill switch"""
        if self.automator.emergency_stop():
            # Update UI state
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            # Make sure the window comes to the front
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

    def create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure root grid to allow expansion
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Button coordinates section
        ttk.Label(main_frame, text="Game Button Coordinates", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 5))

        # Coordinate display
        coord_frame = ttk.Frame(main_frame)
        coord_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)

        # Apply button coordinates
        ttk.Label(coord_frame, text="Apply Button:").grid(row=0, column=0, sticky=tk.W)
        self.apply_coord_var = tk.StringVar(value="Not set")
        ttk.Label(coord_frame, textvariable=self.apply_coord_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Button(coord_frame, text="Set", command=self.set_apply_button).grid(row=0, column=2, padx=5)

        # Change button coordinates
        ttk.Label(coord_frame, text="Change Button:").grid(row=1, column=0, sticky=tk.W)
        self.change_coord_var = tk.StringVar(value="Not set")
        ttk.Label(coord_frame, textvariable=self.change_coord_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Button(coord_frame, text="Set", command=self.set_change_button).grid(row=1, column=2, padx=5)

        # Detection region coordinates
        ttk.Label(coord_frame, text="Detection Region:").grid(row=2, column=0, sticky=tk.W)
        self.detection_region_var = tk.StringVar(value="Not set")
        ttk.Label(coord_frame, textvariable=self.detection_region_var).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Button(coord_frame, text="Set", command=self.set_detection_region).grid(row=2, column=2, padx=5)

        # Offensive stats section
        ttk.Label(main_frame, text="Offensive Stat", font=("Arial", 10, "bold")).grid(
            row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))

        # Get offensive skills from stats_data
        offensive_skills = stats_data.get_offensive_skills()
        offensive_skills.insert(0, "")  # Add empty option

        # Single offensive stat input
        ttk.Label(main_frame, text="Stat:").grid(row=3, column=0, sticky=tk.W)
        self.off_stat = tk.StringVar()

        # Create dropdown menu for stat selection
        self.off_stat_dropdown = ttk.Combobox(main_frame, width=18, textvariable=self.off_stat, state="readonly")
        self.off_stat_dropdown.grid(row=3, column=1, padx=5)
        self.off_stat_dropdown['values'] = offensive_skills

        # Add callback for when stat is selected
        self.off_stat_dropdown.bind("<<ComboboxSelected>>", self.update_off_variations)

        # Add variations dropdown
        ttk.Label(main_frame, text="Variation:").grid(row=3, column=2, sticky=tk.W)
        self.off_var = tk.StringVar()
        self.off_var_dropdown = ttk.Combobox(main_frame, width=8, textvariable=self.off_var, state="readonly")
        self.off_var_dropdown.grid(row=3, column=3, padx=5)

        # Defensive stats section
        ttk.Label(main_frame, text="Defensive/Utility Stat", font=("Arial", 10, "bold")).grid(
            row=4, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))

        # Get defensive skills from stats_data
        defensive_skills = stats_data.get_defensive_skills()
        defensive_skills.insert(0, "")  # Add empty option

        # Single defensive stat input
        ttk.Label(main_frame, text="Stat:").grid(row=5, column=0, sticky=tk.W)
        self.def_stat = tk.StringVar()

        # Create dropdown menu for stat selection
        self.def_stat_dropdown = ttk.Combobox(main_frame, width=18, textvariable=self.def_stat, state="readonly")
        self.def_stat_dropdown.grid(row=5, column=1, padx=5)
        self.def_stat_dropdown['values'] = defensive_skills

        # Add callback for when stat is selected
        self.def_stat_dropdown.bind("<<ComboboxSelected>>", self.update_def_variations)

        # Add variations dropdown
        ttk.Label(main_frame, text="Variation:").grid(row=5, column=2, sticky=tk.W)
        self.def_var = tk.StringVar()
        self.def_var_dropdown = ttk.Combobox(main_frame, width=8, textvariable=self.def_var, state="readonly")
        self.def_var_dropdown.grid(row=5, column=3, padx=5)

        # Status section
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9)).grid(
            row=6, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))

        # Log section
        ttk.Label(main_frame, text="Session Log", font=("Arial", 10, "bold")).grid(
            row=7, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))

        # Create a frame for the log with scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Configure the log frame to expand
        main_frame.rowconfigure(8, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget for logs
        self.log_text = tk.Text(log_frame, height=10, width=40, wrap=tk.WORD,
                               yscrollcommand=scrollbar.set, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Clear any existing text
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Make the text widget read-only
        self.log_text.config(state=tk.DISABLED)

        # Kill switch info
        kill_switch_label = ttk.Label(main_frame, text="Emergency Stop: Press ESC key anytime",
                                     foreground="red", font=("Arial", 9, "bold"))
        kill_switch_label.grid(row=9, column=0, columnspan=4, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=4, pady=10)

        # Start/Stop buttons
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_automation)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Add padding to all widgets
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=2)

    def set_button_coords(self, button_type):
        """Record the coordinates of a game button"""
        self.update_status(f"Click on the {button_type} button in the game")
        self.root.config(cursor="crosshair")  # Change cursor to indicate click mode

        # Connect to game if needed
        if not self.game_connector.is_connected():
            self.game_connector.connect_to_game()

        # Function to capture mouse click
        def capture_click():
            # Wait for next mouse click
            mouse.wait(button='left')

            # Get mouse position
            x, y = mouse.get_position()

            # Get game window position
            rect = self.game_connector.get_window_rect()
            if rect:
                # Calculate relative coordinates
                rel_x = x - rect.left
                rel_y = y - rect.top

                # Store coordinates based on button type
                if button_type == "Apply":
                    self.apply_button_coords = (rel_x, rel_y)
                    self.apply_coord_var.set(f"({rel_x}, {rel_y})")
                else:  # Change button
                    self.change_button_coords = (rel_x, rel_y)
                    self.change_coord_var.set(f"({rel_x}, {rel_y})")

                self.update_status(f"{button_type} button set at: ({rel_x}, {rel_y})")
            else:
                self.update_status("Failed to get game window position")

            # Reset cursor
            self.root.config(cursor="")

        # Start the capture in a thread so it doesn't block the UI
        thread = threading.Thread(target=capture_click, daemon=True)
        thread.start()

    def set_apply_button(self):
        """Set Apply button coordinates"""
        self.set_button_coords("Apply")

    def set_change_button(self):
        """Set Change button coordinates"""
        self.set_button_coords("Change")



    def start_automation(self):
        """Start the automation process"""
        # Check if at least one stat is specified
        if not self.off_stat.get() and not self.def_stat.get():
            messagebox.showerror("Error", "Please specify at least one stat to look for.")
            return

        # Prepare desired stats
        desired_stats = {
            'offensive': [],
            'defensive': []
        }

        # Add offensive stat if specified
        stat_name = self.off_stat.get()
        if stat_name:
            variation = self.off_var.get()
            if not variation:
                messagebox.showerror("Error", f"Please select a variation for {stat_name}.")
                return

            # Extract numeric value from the variation
            value_match = re.search(r'(\d+)', variation)
            if value_match:
                off_val = int(value_match.group(1))
                desired_stats['offensive'].append((stat_name, off_val, variation))
                self.update_status(f"Looking for {stat_name} with variation {variation}")

        # Add defensive stat if specified
        stat_name = self.def_stat.get()
        if stat_name:
            variation = self.def_var.get()
            if not variation:
                messagebox.showerror("Error", f"Please select a variation for {stat_name}.")
                return

            # Extract numeric value from the variation
            value_match = re.search(r'(\d+)', variation)
            if value_match:
                def_val = int(value_match.group(1))
                desired_stats['defensive'].append((stat_name, def_val, variation))
                self.update_status(f"Looking for {stat_name} with variation {variation}")

        # Start the automation (always in performance mode)
        if self.automator.start(self.apply_button_coords, self.change_button_coords, desired_stats):
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_automation(self):
        """Stop the automation process"""
        self.automator.stop()
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Make sure the window comes to the front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)

    def set_detection_region(self):
        """Allow user to select a region of the screen"""
        self.update_status("Click and drag to select the region with stats")

        # Create a simple transparent overlay
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.2)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='grey')

        # Variables for selection
        start_x, start_y = 0, 0
        rect = None

        # Handle mouse events
        def on_press(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            rect = tk.Canvas(overlay, bg='red', height=1, width=1)
            rect.place(x=start_x, y=start_y)

        def on_drag(event):
            nonlocal rect, start_x, start_y
            width = abs(event.x - start_x)
            height = abs(event.y - start_y)
            x = min(start_x, event.x)
            y = min(start_y, event.y)
            rect.place(x=x, y=y, width=width, height=height)

        def on_release(event):
            left = min(start_x, event.x)
            top = min(start_y, event.y)
            right = max(start_x, event.x)
            bottom = max(start_y, event.y)

            self.detection_region = (left, top, right, bottom)
            self.detection_region_var.set(f"({left}, {top}, {right}, {bottom})")
            self.automator.set_detection_region(self.detection_region)
            self.update_status(f"Region set: ({left}, {top}, {right}, {bottom})")

            overlay.destroy()

        # Bind events
        overlay.bind("<ButtonPress-1>", on_press)
        overlay.bind("<B1-Motion>", on_drag)
        overlay.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", lambda _: overlay.destroy())

    def update_off_variations(self, event=None):
        """Update the offensive stat variations dropdown based on selected stat"""
        selected_stat = self.off_stat.get()
        if selected_stat:
            variations = stats_data.get_stat_variations(selected_stat)
            self.off_var_dropdown['values'] = variations
            if variations:
                self.off_var.set(variations[0])  # Select first variation by default
        else:
            self.off_var_dropdown['values'] = []
            self.off_var.set("")

    def update_def_variations(self, event=None):
        """Update the defensive stat variations dropdown based on selected stat"""
        selected_stat = self.def_stat.get()
        if selected_stat:
            variations = stats_data.get_stat_variations(selected_stat)
            self.def_var_dropdown['values'] = variations
            if variations:
                self.def_var.set(variations[0])  # Select first variation by default
        else:
            self.def_var_dropdown['values'] = []
            self.def_var.set("")

    def on_closing(self):
        """Clean up resources when the window is closed"""
        # Unregister the hotkey to prevent it from persisting after the app closes
        keyboard.unhook_all()
        self.root.destroy()