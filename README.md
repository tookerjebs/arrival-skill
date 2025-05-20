# Skill Reroll Automation Tool

A lightweight automation tool for rerolling skills in Cabal Online. This tool uses Python for mouse input and text recognition to identify game stats.

## Features

- Automatically clicks Apply and Change buttons to reroll skills
- Uses PaddleOCR for lightweight and accurate text recognition
- Detects both offensive and defensive stats
- Customizable target stats with variation selection
- Emergency stop with ESC key
- Session logging with detailed stat detection information

## Requirements

- Python 3.8+
- PaddleOCR
- PyWinAuto
- Tkinter
- Keyboard and Mouse libraries

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Usage

1. **Setting Up Button Coordinates**:
   - Click "Set Apply Button" and then click on the Apply button in the game
   - Click "Set Change Button" and then click on the Change button in the game
   - Set the detection region by clicking "Set" and selecting the area with stats

2. **Selecting Desired Stats**:
   - Choose stats from the dropdown menus
   - Select the desired variation for each stat
   - At least one stat must be selected

3. **Running the Automation**:
   - Click "Start" to begin the automation
   - The tool will click the Change button until desired stats are found
   - Press ESC at any time to stop the automation (emergency kill switch)

## Project Structure

- **main.py**: Entry point that initializes the application
- **ui.py**: Handles the user interface components
- **game_connector.py**: Manages connecting to the game window and sending clicks
- **stats_data.py**: Contains data about available skills and their values
- **automation.py**: Implements the automation logic
- **paddle_ocr_implementation.py**: Handles text recognition using PaddleOCR

## License

This project is licensed under the MIT License - see the LICENSE file for details.
