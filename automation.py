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
        self.detailed_logging = False

        # Initialize PaddleOCR reader - lazy initialization to speed up startup
        self.reader = None

        # Initialize stat counter for tracking stats across rolls
        self.stat_counter = {}

        # Initialize unmapped OCR results counter
        self.unmapped_ocr_counter = {}

        self.update_status("PaddleOCR will be initialized when automation starts")

    def set_detection_region(self, region):
        """Set the region for text detection"""
        self.detection_region = region
        self.update_status(f"Detection region set to {region}")

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def start(self, apply_coords, change_coords, desired_stats=None, detailed_logging=False):
        """Start the automation with optional detailed logging"""
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
        self.detailed_logging = detailed_logging

        # Reset counters for new run
        self.unmapped_ocr_counter = {}

        # Log startup message
        if detailed_logging:
            self.update_status("Starting automation with detailed logging")
        else:
            self.update_status("Starting automation (minimal logging mode)")

        # Always reinitialize PaddleOCR reader to ensure a clean state
        try:
            self.update_status("Initializing PaddleOCR...")
            # First make sure any existing reader is cleaned up
            self.reader = None
            # Create a fresh instance
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
        """Stop the automation, clean up resources, and show stats summary"""
        self.running = False

        # Clean up OCR reader to prevent errors on restart
        if hasattr(self, 'reader') and self.reader is not None:
            self.reader = None

        self.update_status("⏹️ Automation stopped")

        # Show summary of stats if we have any
        if hasattr(self, 'stat_counter') and self.stat_counter:
            self.update_status("")
            self.update_status("SUMMARY OF DETECTED STATS")

            # Separate stats by category
            from stats_data import get_offensive_skills, get_defensive_skills, get_base_stat_name

            offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
            defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

            # Group stats by category
            offensive_stats = {}
            defensive_stats = {}
            other_stats = {}

            for stat_key, count in self.stat_counter.items():
                # Extract the stat name from the key (format is "stat_name +value")
                parts = stat_key.split("+")
                if len(parts) >= 1:
                    stat_name = parts[0].strip()

                    # Categorize the stat
                    if stat_name in offensive_base_stats:
                        offensive_stats[stat_key] = count
                    elif stat_name in defensive_base_stats:
                        defensive_stats[stat_key] = count
                    else:
                        other_stats[stat_key] = count

            # Display offensive stats
            if offensive_stats:
                self.update_status("Offensive Stats:")
                for stat_key, count in sorted(offensive_stats.items(), key=lambda x: x[1], reverse=True):
                    self.update_status(f"  • {stat_key} × {count}")

            # Display defensive stats
            if defensive_stats:
                self.update_status("Defensive Stats:")
                for stat_key, count in sorted(defensive_stats.items(), key=lambda x: x[1], reverse=True):
                    self.update_status(f"  • {stat_key} × {count}")

            # Display other stats
            if other_stats:
                self.update_status("Other Stats:")
                for stat_key, count in sorted(other_stats.items(), key=lambda x: x[1], reverse=True):
                    self.update_status(f"  • {stat_key} × {count}")

            # Display unmapped OCR results if any
            if hasattr(self, 'unmapped_ocr_counter') and self.unmapped_ocr_counter:
                self.update_status("")
                self.update_status("Unmapped OCR Results:")

                # Sort by frequency (most common first)
                sorted_unmapped = sorted(self.unmapped_ocr_counter.items(), key=lambda x: x[1], reverse=True)

                # Display top 10 unmapped results
                for text, count in sorted_unmapped[:10]:
                    if len(text.strip()) > 0:  # Skip empty strings
                        self.update_status(f"  • '{text}' × {count}")

            # Reset the counters for next run
            self.stat_counter = {}
            self.unmapped_ocr_counter = {}

    def capture_screen_region(self):
        """Capture a screenshot of the detection region or the game window with optimized performance"""
        if not self.game_connector.is_connected():
            return None

        # Cache the region to avoid recalculating it on every capture
        if not hasattr(self, '_cached_region') or self._cached_region is None:
            # If detection region is set, use it, otherwise capture the full game window
            if self.detection_region:
                self._cached_region = self.detection_region
            else:
                rect = self.game_connector.get_window_rect()
                if not rect:
                    return None
                self._cached_region = (rect.left, rect.top, rect.right, rect.bottom)

        # Capture the screen region with optimized settings
        try:
            # Use all_screens=False for faster capture if we know we're only capturing the primary screen
            return ImageGrab.grab(bbox=self._cached_region, all_screens=False)
        except Exception:
            # Reset cached region on error
            self._cached_region = None
            return None

    def detect_text_in_image(self, image):
        """Simplified method to detect text in the image using PaddleOCR"""
        if self.reader is None:
            self.update_status("OCR reader not initialized")
            return {}

        # Get text from image - error handling is now done in the readtext method
        results = self.reader.readtext(image)

        # Skip processing if no text was detected
        if not results:
            return {}

        # Parse the detected text to find stats and values
        current_stats = parse_detected_text(
            results,
            self.update_status,
            detailed_logging=self.detailed_logging,
            unmapped_ocr_counter=self.unmapped_ocr_counter
        )
        return current_stats

    def reroll_loop(self, desired_stats):
        """Optimized main reroll loop that checks for desired stats with fast-path processing"""
        self.update_status("▶️ Starting automation...")

        # Track iterations for performance optimization
        iteration_count = 0

        # Initialize stat counter if it doesn't exist
        if not hasattr(self, 'stat_counter'):
            self.stat_counter = {}

        # First click the Change button to remove the current option
        self.game_connector.click_at_position(self.change_button_coords)
        time.sleep(0.4)  # Reduced from 0.8s to 0.4s

        # Import stats categories once outside the loop
        from stats_data import get_offensive_skills, get_defensive_skills, get_base_stat_name

        # Pre-compute these sets once outside the loop
        offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
        defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

        while self.running:
            iteration_count += 1

            # Click Apply button to apply a new option
            self.game_connector.click_at_position(self.apply_button_coords)
            time.sleep(0.5)  # Minimum time needed for the game to update

            # Capture the game screen
            screenshot = self.capture_screen_region()
            if screenshot is None:
                self.update_status("Failed to capture screen, retrying...")
                time.sleep(0.5)  # Reduced wait time
                continue

            # Detect text in the screenshot
            if self.reader:
                current_stats = self.detect_text_in_image(screenshot)

                # Only log roll information in detailed mode
                if self.detailed_logging:
                    self.update_status(f"Roll #{iteration_count}")

                if current_stats:
                    # Prepare a concise summary of detected stats
                    off_stats = [(stat, current_stats[stat]) for stat in current_stats if stat in offensive_base_stats]
                    def_stats = [(stat, current_stats[stat]) for stat in current_stats if stat in defensive_base_stats]
                    other_stats = [(stat, current_stats[stat]) for stat in current_stats
                                  if stat not in offensive_base_stats and stat not in defensive_base_stats]

                    # Track stats for summary regardless of logging mode

                    # Track offensive stats
                    for stat, value in off_stats:
                        # Track stats for summary with plus sign
                        stat_key = f"{stat} +{value}"
                        self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1

                    # Track defensive stats
                    for stat, value in def_stats:
                        # Track stats for summary with plus sign
                        stat_key = f"{stat} +{value}"
                        self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1

                    # Track other stats
                    for stat, value in other_stats:
                        # Track stats for summary with plus sign
                        stat_key = f"{stat} +{value}"
                        self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1

                    # Only log stats in detailed mode
                    if self.detailed_logging:
                        # Log all stats in a single block
                        all_stats = []

                        # Add offensive stats
                        if off_stats:
                            for stat, value in off_stats:
                                all_stats.append(f"{stat}: {value}")

                        # Add defensive stats
                        if def_stats:
                            for stat, value in def_stats:
                                all_stats.append(f"{stat}: {value}")

                        # Add other stats
                        if other_stats:
                            for stat, value in other_stats:
                                all_stats.append(f"{stat}: {value}")

                        # Log all stats in a single line if possible
                        if all_stats:
                            self.update_status(" | ".join(all_stats))
                elif self.detailed_logging:
                    self.update_status("No stats detected")
            else:
                current_stats = {}
                self.update_status("OCR reader not initialized")

            # Check if we have desired stats
            if self.check_desired_stats(current_stats, desired_stats):
                self.update_status("🎉🎉🎉 SUCCESS! DESIRED STATS FOUND! 🎉🎉🎉")
                self.stop()  # Stop automation and clean up resources
                messagebox.showinfo("Success", "Desired stats found! Automation stopped.")
                break

            # If desired stats not found, click the Change button to reroll
            self.game_connector.click_at_position(self.change_button_coords)
            time.sleep(0.4)  # Minimum time needed for the game to respond

    def check_desired_stats(self, current_stats, desired_stats):
        """
        Check if current stats meet the desired criteria:
        - If only offensive stat specified: The offensive stat must be found
        - If only defensive stat specified: The defensive stat must be found
        - If both are specified: Both the offensive AND defensive stat must be found
        - If a variation is specified, it will be used for additional logging but not for matching
        """
        # Import the base stat name function
        from stats_data import get_base_stat_name

        # If no desired stats specified at all, return True
        if not desired_stats['offensive'] and not desired_stats['defensive']:
            return True

        # Store match information to display only if overall match is successful
        match_messages = []

        # Check if offensive stat matches (if specified)
        off_match = False
        off_stat_info = None
        if desired_stats['offensive']:
            # Unpack the stat info
            display_stat_name, min_value, _ = desired_stats['offensive'][0]
            off_stat_info = (display_stat_name, min_value)

            # Get the base stat name for OCR detection
            base_stat_name = get_base_stat_name(display_stat_name)

            if base_stat_name in current_stats and current_stats[base_stat_name] >= min_value:
                off_match = True
                match_messages.append(f"✅ MATCH: Found {display_stat_name} with value {current_stats[base_stat_name]} (target: {min_value}+)")
        else:
            # No offensive stat specified, so consider it a match
            off_match = True

        # Check if defensive stat matches (if specified)
        def_match = False
        def_stat_info = None
        if desired_stats['defensive']:
            # Unpack the stat info
            display_stat_name, min_value, _ = desired_stats['defensive'][0]
            def_stat_info = (display_stat_name, min_value)

            # Get the base stat name for OCR detection
            base_stat_name = get_base_stat_name(display_stat_name)

            if base_stat_name in current_stats and current_stats[base_stat_name] >= min_value:
                def_match = True
                match_messages.append(f"✅ MATCH: Found {display_stat_name} with value {current_stats[base_stat_name]} (target: {min_value}+)")
        else:
            # No defensive stat specified, so consider it a match
            def_match = True

        # Only show match messages if both conditions are met
        # or if only one stat type was specified and it matched
        overall_match = off_match and def_match

        # Only display success messages if we have an overall match
        # or if only one stat type was specified (not both)
        if overall_match:
            # If both stat types were specified, show all match messages
            for message in match_messages:
                self.update_status(message)

        # Need both conditions to be true
        return overall_match

    def emergency_stop(self):
        """Emergency stop function triggered by kill switch"""
        if self.running:
            # Use the regular stop method to ensure proper cleanup
            self.stop()
            self.update_status("⚠️ EMERGENCY STOP: Automation stopped by ESC key ⚠️")
            messagebox.showinfo("Emergency Stop", "Automation stopped by pressing the ESC key")
            return True
        return False
