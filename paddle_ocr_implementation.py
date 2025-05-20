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

def calculate_string_similarity(str1, str2):
    """
    Calculate similarity between two strings based on character matching and length.
    Returns a score between 0 and 1, where 1 is a perfect match.
    """
    # If either string is empty, return 0
    if not str1 or not str2:
        return 0

    # If strings are identical, return 1
    if str1 == str2:
        return 1

    # Calculate character-by-character matches
    char_matches = 0
    for char in str1:
        if char in str2:
            char_matches += 1

    # Calculate similarity based on:
    # 1. Percentage of matching characters
    # 2. Length difference penalty
    max_length = max(len(str1), len(str2))

    # Basic character similarity
    char_similarity = char_matches / max_length

    # Length difference penalty - penalize matches where lengths are very different
    # This helps distinguish between "Defense" and "Defense Rate"
    length_diff = abs(len(str1) - len(str2)) / max(len(str1), len(str2))
    length_penalty = length_diff * 0.5  # Apply 50% weight to length difference

    # Final similarity score
    similarity = char_similarity - length_penalty

    # Ensure the result is between 0 and 1
    return max(0, min(similarity, 1))

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

        # Special case for "Arrival skill Cool time decreased" which often gets detected with its value
        # Check for various possible OCR variations of this text
        if "arrival" in text.lower() and "cool" in text.lower() and "time" in text.lower():
            # Extract the stat name part
            stat_name = "Arrival Skill Cool Time decreased."

            # Try to extract the value part
            value_match = re.search(r'(\d+)[s]?', text)
            if value_match:
                value = int(value_match.group(1))

                # Add both the stat and its value
                stats_with_y.append((y_center, stat_name, stat_name))
                values_with_y.append((y_center, text, value))

                if status_callback:
                    status_callback(f"Special case: Split '{text}' into stat '{stat_name}' and value {value}")
                continue

        # Check if this text contains a value - improved pattern to catch more variations
        # Including % for percentage values and s for seconds (used in Arrival Skill Cool Time)
        value_match = re.search(r'[+]?(\d+)(?:[%s])?', text)
        if value_match:
            value = int(value_match.group(1))
            values_with_y.append((y_center, text, value))
            if status_callback:
                status_callback(f"Found value: {value} in '{text}'")
            continue

        # Normalize the detected text
        norm_text = normalize_text(text)

        # Find the best matching stat based on string similarity
        best_match = None
        best_similarity = 0.0

        for norm_stat, original_stat in normalized_stats.items():
            # Calculate similarity between normalized detected text and normalized stat
            similarity = calculate_string_similarity(norm_text, norm_stat)

            # If this is the best match so far, remember it
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = original_stat

        # Only consider it a match if similarity is above a threshold (0.6)
        # This threshold is adjusted for our simplified similarity function
        if best_match and best_similarity >= 0.6:
            stats_with_y.append((y_center, text, best_match))
            if status_callback:
                status_callback(f"Matched '{text}' to '{best_match}' (similarity: {best_similarity:.2f})")
                # Log whether it's offensive or defensive
                if best_match in offensive_stats:
                    status_callback(f"'{best_match}' is an offensive stat")
                elif best_match in defensive_stats:
                    status_callback(f"'{best_match}' is a defensive stat")

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
