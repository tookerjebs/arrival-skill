"""
Ultra-lightweight PaddleOCR implementation for the Skill Reroll Automation tool.
"""

import numpy as np
from PIL import Image
import re
from paddleocr import PaddleOCR

class PaddleOCRWrapper:
    def __init__(self, status_callback=None):
        # Initialize with minimal settings for speed and lightweight operation
        self.ocr = PaddleOCR(
            use_angle_cls=False,  # Disable angle classification for speed
            lang='en',            # English language
            use_gpu=True,         # Use GPU for faster processing
            show_log=False,       # Disable logs
            enable_mkldnn=True    # Enable Intel MKL-DNN acceleration
        )
        self.status_callback = status_callback

    def readtext(self, image):
        """Convert image to text using PaddleOCR"""
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Run OCR
        result = self.ocr.ocr(image, cls=False)  # Disable classifier for speed
        detected_items = []

        # Process results
        if result and len(result) > 0:
            for line in result[0]:
                if len(line) >= 2:
                    box = line[0]
                    text = line[1][0]
                    confidence = line[1][1]
                    detected_items.append((box, text, confidence))

        return detected_items

def normalize_text(text):
    """Normalize text by converting to lowercase and removing spaces and dots"""
    return text.lower().replace(" ", "").replace(".", "")

def get_y_center(box):
    """Calculate the y-center of a bounding box"""
    # Box format is [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
    if not box or len(box) != 4:
        return 0
    return (box[0][1] + box[2][1]) / 2

def parse_detected_text(detected_items, status_callback=None):
    """
    Simplified parser to find stats and values using y-coordinates for matching.
    detected_items: List of tuples (box, text, confidence) from OCR
    """
    found_stats = {}

    # Get stat names from stats_data module
    from stats_data import get_all_skills, get_offensive_skills, get_defensive_skills, get_base_stat_name

    # Get the base stat names for OCR detection
    stat_names = get_all_skills()
    offensive_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
    defensive_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

    # Create normalized versions of stat names for matching
    normalized_stats = {normalize_text(stat): stat for stat in stat_names}

    if status_callback:
        status_callback(f"Processing {len(detected_items)} text elements")

    # Identify stats and values with their y-coordinates
    stats_with_y = []  # (y_center, text, stat_name)
    values_with_y = []  # (y_center, text, value)

    # Debug all detected text
    if status_callback:
        for _, text, _ in detected_items:
            status_callback(f"Raw detected text: '{text}'")

    for box, text, _ in detected_items:
        # Get the y-center of this text
        y_center = get_y_center(box)

        # Check if this text contains a value - improved pattern to catch more variations
        value_match = re.search(r'[+]?(\d+)[%]?', text)
        if value_match:
            value = int(value_match.group(1))
            values_with_y.append((y_center, text, value))
            if status_callback:
                status_callback(f"Found value: {value} in '{text}'")
            continue

        # Normalize the detected text
        norm_text = normalize_text(text)

        # Check if this normalized text matches any of our normalized stat names
        for norm_stat, original_stat in normalized_stats.items():
            # More flexible matching - check if normalized stat is in normalized text
            # or if normalized text is in normalized stat (for partial matches)
            if norm_stat in norm_text or (len(norm_text) > 3 and norm_text in norm_stat):
                stats_with_y.append((y_center, text, original_stat))
                if status_callback:
                    status_callback(f"Matched '{text}' to '{original_stat}'")
                    # Log whether it's offensive or defensive
                    if original_stat in offensive_stats:
                        status_callback(f"'{original_stat}' is an offensive stat")
                    elif original_stat in defensive_stats:
                        status_callback(f"'{original_stat}' is a defensive stat")
                break

    # For each stat, find the value with the closest y-coordinate
    for stat_y, _, stat_name in stats_with_y:
        closest_value = None
        min_distance = float('inf')

        for value_y, _, value in values_with_y:
            # Calculate vertical distance between stat and value
            distance = abs(stat_y - value_y)

            # If this is the closest value so far, remember it
            if distance < min_distance:
                min_distance = distance
                closest_value = value

        # If we found a value within a reasonable distance (e.g., 50 pixels - increased from 30)
        if closest_value is not None and min_distance < 50:
            found_stats[stat_name] = closest_value
            if status_callback:
                status_callback(f"Paired '{stat_name}' with {closest_value}")

    return found_stats
