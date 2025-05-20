"""
Automation module for the Skill Reroll Automation tool.
This version uses PaddleOCR for more reliable and lightweight text recognition.
"""

import time
import threading
from tkinter import messagebox
from PIL import ImageGrab
from paddle_ocr_implementation import PaddleOCRWrapper, parse_detected_text

class SkillRerollAutomator:
    def __init__(self, game_connector, status_callback=None):
        """Initialize the skill reroll automator"""
        self.game_connector = game_connector
        self.status_callback = status_callback
        self.running = False
        self.apply_button_coords = None
        self.change_button_coords = None
        self.detection_region = None

        # Initialize PaddleOCR reader
        try:
            self.update_status("Initializing PaddleOCR...")
            self.reader = PaddleOCRWrapper(self.update_status)
        except Exception as e:
            self.update_status(f"Error initializing PaddleOCR: {str(e)}")
            self.reader = None

    def set_detection_region(self, region):
        """Set the region for text detection"""
        self.detection_region = region
        self.update_status(f"Detection region set to {region}")

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def start(self, apply_coords, change_coords, desired_stats=None):
        """Start the automation"""
        # Check if button coordinates are set
        if not apply_coords or not change_coords:
            messagebox.showerror("Error", "Please set both Apply and Change button coordinates.")
            return False

        # Connect to the game if not already connected
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                return False

        # Store button coordinates
        self.apply_button_coords = apply_coords
        self.change_button_coords = change_coords

        # Reinitialize PaddleOCR reader to ensure fresh state
        try:
            self.update_status("Reinitializing PaddleOCR...")
            self.reader = PaddleOCRWrapper(self.update_status)
        except Exception as e:
            self.update_status(f"Error initializing PaddleOCR: {str(e)}")
            self.reader = None
            return False

        # Start the automation thread
        self.running = True
        threading.Thread(target=self.reroll_loop, args=(desired_stats,), daemon=True).start()

        return True

    def stop(self):
        """Stop the automation"""
        self.running = False
        self.update_status("⏹️ Automation stopped")

    def capture_screen_region(self):
        """Capture a screenshot of the detection region or the game window"""
        if not self.game_connector.is_connected():
            return None

        # If detection region is set, use it, otherwise capture the full game window
        if self.detection_region:
            region = self.detection_region
        else:
            rect = self.game_connector.get_window_rect()
            if not rect:
                return None
            region = (rect.left, rect.top, rect.right, rect.bottom)

        # Capture the screen region
        try:
            return ImageGrab.grab(bbox=region)
        except Exception:
            return None

    def detect_text_in_image(self, image):
        """Simplified method to detect text in the image using PaddleOCR"""
        if self.reader is None or self.reader.ocr is None:
            self.update_status("OCR reader not initialized")
            return {}

        try:
            # Get text from image
            results = self.reader.readtext(image)

            # Filter results by confidence (only keep results with >50% confidence)
            filtered_results = [(box, text, prob) for box, text, prob in results if prob > 0.5]

            # Parse the detected text to find stats and values
            current_stats = parse_detected_text(filtered_results, self.update_status)
            return current_stats

        except Exception as e:
            self.update_status(f"OCR error: {str(e)}")
            return {}

    def reroll_loop(self, desired_stats):
        """Simplified main reroll loop that checks for desired stats"""
        self.update_status("▶️ Starting automation...")

        # First click the Change button to remove the current option
        self.game_connector.click_at_position(self.change_button_coords)
        time.sleep(0.8)

        while self.running:
            # Click Apply button to apply a new option
            self.game_connector.click_at_position(self.apply_button_coords)
            time.sleep(1.0)

            # Capture the game screen
            screenshot = self.capture_screen_region()
            if screenshot is None:
                self.update_status("Failed to capture screen, retrying...")
                time.sleep(1)
                continue

            # Detect text in the screenshot
            if self.reader:
                current_stats = self.detect_text_in_image(screenshot)

                # Log all detected stats with their values
                if current_stats:
                    # Import stats categories
                    from stats_data import get_offensive_skills, get_defensive_skills
                    offensive_stats = get_offensive_skills()
                    defensive_stats = get_defensive_skills()

                    # Create formatted log entries
                    self.update_status("--- New Roll ---")

                    # Log offensive stats
                    found_offensive = [(stat, current_stats[stat]) for stat in current_stats if stat in offensive_stats]
                    if found_offensive:
                        self.update_status("Offensive stats:")
                        for stat, value in found_offensive:
                            self.update_status(f"  • {stat}: {value}")

                    # Log defensive stats
                    found_defensive = [(stat, current_stats[stat]) for stat in current_stats if stat in defensive_stats]
                    if found_defensive:
                        self.update_status("Defensive stats:")
                        for stat, value in found_defensive:
                            self.update_status(f"  • {stat}: {value}")

                    # Log any unrecognized stats
                    other_stats = [(stat, current_stats[stat]) for stat in current_stats
                                  if stat not in offensive_stats and stat not in defensive_stats]
                    if other_stats:
                        self.update_status("Other stats:")
                        for stat, value in other_stats:
                            self.update_status(f"  • {stat}: {value}")
                else:
                    self.update_status("No stats detected in this frame")
            else:
                current_stats = {}
                self.update_status("OCR reader not initialized")

            # Check if we have desired stats
            if self.check_desired_stats(current_stats, desired_stats):
                self.update_status("🎉 SUCCESS: All desired stats found! 🎉")
                messagebox.showinfo("Success", "Desired stats found!")
                self.stop()
                break

            # If desired stats not found, click the Change button to reroll
            self.game_connector.click_at_position(self.change_button_coords)
            time.sleep(0.8)

    def check_desired_stats(self, current_stats, desired_stats):
        """
        Check if current stats meet the desired criteria:
        - If only offensive stat specified: The offensive stat must be found
        - If only defensive stat specified: The defensive stat must be found
        - If both are specified: Both the offensive AND defensive stat must be found
        - If a variation is specified, it will be used for additional logging but not for matching
        """
        # If no desired stats specified at all, return True
        if not desired_stats['offensive'] and not desired_stats['defensive']:
            return True

        # Check if offensive stat matches (if specified)
        off_match = False
        if desired_stats['offensive']:
            # Unpack the stat info (includes variation)
            stat_name, min_value, variation = desired_stats['offensive'][0]

            if stat_name in current_stats and current_stats[stat_name] >= min_value:
                off_match = True
                self.update_status(f"✓ MATCH: Offensive stat {stat_name} = {current_stats[stat_name]}" +
                                  (f" (target: {variation})" if variation else ""))
        else:
            # No offensive stat specified, so consider it a match
            off_match = True

        # Check if defensive stat matches (if specified)
        def_match = False
        if desired_stats['defensive']:
            # Unpack the stat info (includes variation)
            stat_name, min_value, variation = desired_stats['defensive'][0]

            if stat_name in current_stats and current_stats[stat_name] >= min_value:
                def_match = True
                self.update_status(f"✓ MATCH: Defensive stat {stat_name} = {current_stats[stat_name]}" +
                                  (f" (target: {variation})" if variation else ""))
        else:
            # No defensive stat specified, so consider it a match
            def_match = True

        # Need both conditions to be true
        return off_match and def_match

    def emergency_stop(self):
        """Emergency stop function triggered by kill switch"""
        if self.running:
            self.running = False
            self.update_status("⚠️ EMERGENCY STOP: Automation stopped by ESC key")
            messagebox.showinfo("Emergency Stop", "Automation stopped by kill switch (ESC key)")
            return True
        return False
