"""
Stats data module for the Skill Reroll Automation tool.
"""

# Known skill options
KNOWN_SKILLS = [
    # Original skills
    "All Skill Amp.",
    "Ignore Resist Skill Amp.",
    "All Attack Up.",
    "Add. Damage",
    "HP Auto Heal",
    "Absorb Damage",
    "HP Absorb Up",
    "Max HP Steal per Hit",

    # Force Wings skills from images
    "Crit. DMG",
    "Ignore Resist Crit. DMG",
    "Defense",
    "DMG Reduction",
    "Arrival Skill Cooldown Reduce",
    "Ignore Resist Crit. Rate",
    "Ignore Evasion",
    "Attack Rate",
    "Resist Skill Amp.",
    "Heal",
    "Ignore Accuracy",
    "Defense Rate",
    "Arrival Skill Duration Increase",
    "Max Crit. Rate",
    "Accuracy",
    "Resist Crit. DMG",
    "Evasion",
    "Penetration",
    "Cancel Ignore Penetration",
    "Normal DMG Up",
    "Ignore Penetration",
    "Damage Absorb",
    "PvE Resist Skill Amp.",
    "PvE Resist Crit. DMG"
]

# Categorize skills
OFFENSIVE_SKILLS = [
    # Original offensive skills
    "All Skill Amp.",
    "Ignore Resist Skill Amp.",
    "All Attack Up.",
    "Add. Damage",

    # New offensive skills
    "Crit. DMG",
    "Ignore Resist Crit. DMG",
    "Ignore Resist Crit. Rate",
    "Ignore Evasion",
    "Attack Rate",
    "Resist Skill Amp.",
    "Ignore Accuracy",
    "Max Crit. Rate",
    "Accuracy",
    "Penetration",
    "Cancel Ignore Penetration",
    "Normal DMG Up",
    "Ignore Penetration"
]

DEFENSIVE_SKILLS = [
    # Original defensive skills
    "HP Auto Heal",
    "Absorb Damage",
    "HP Absorb Up",
    "Max HP Steal per Hit",

    # New defensive skills
    "Defense",
    "DMG Reduction",
    "Arrival Skill Cooldown Reduce",
    "Heal",
    "Defense Rate",
    "Arrival Skill Duration Increase",
    "Resist Crit. DMG",
    "Evasion",
    "Damage Absorb",
    "PvE Resist Skill Amp.",
    "PvE Resist Crit. DMG"
]

# Stat variations with their possible values
STAT_VARIATIONS = {
    # First image stats
    "All Skill Amp.": ["4%", "8%", "16%"],
    "Ignore Resist Skill Amp.": ["3%", "5%", "9%"],
    "All Attack Up.": ["15", "30", "45", "60", "75"],
    "Add. Damage": ["15", "30", "45", "60", "75"],
    "HP Auto Heal": ["120", "240", "500"],
    "Absorb Damage": ["600", "1,200", "2,400"],
    "HP Absorb Up": ["1%", "2%", "3%", "4%", "5%"],
    "Max HP Steal per Hit": ["6", "12", "18", "24", "30"],
    "Crit. DMG": ["9%", "18%", "36%"],
    "Ignore Resist Crit. DMG": ["6%", "11%", "20%"],
    "Defense": ["100", "200", "400"],
    "DMG Reduction": ["15", "30", "45", "60", "75"],

    # Second image stats
    "Arrival Skill Cooldown Reduce": ["15s", "30s", "60s", "120s"],
    "Ignore Resist Crit. Rate": ["1%", "2%"],
    "Ignore Evasion": ["100", "200", "300", "400", "500"],
    "Attack Rate": ["100", "200", "300", "400", "500"],
    "Resist Skill Amp.": ["8%", "15%", "30%"],
    "Heal": ["200", "400", "600", "900"],
    "Ignore Accuracy": ["80", "160", "240", "320", "400"],
    "Defense Rate": ["80", "160", "240", "320", "400", "90", "180", "270", "360", "450"],
    "Arrival Skill Duration Increase (before EP36)": ["2s", "4s", "8s", "15s"],
    "Arrival Skill Duration Increase (after EP36)": ["4s", "8s", "16s", "30s"],
    "Max Crit. Rate": ["1%", "2%"],
    "Accuracy": ["120", "240", "300", "360", "480", "600"],
    "Resist Crit. DMG": ["18%", "35%", "70%"],
    "Evasion": ["90", "180", "270", "360", "450"],

    # Third image stats
    "Penetration": ["30", "65", "130"],
    "Cancel Ignore Penetration": ["18", "35", "75"],
    "Normal DMG Up": ["8%", "16%", "24%", "32%", "40%"],
    "Ignore Penetration": ["50", "100", "200"],
    "Damage Absorb": ["900", "1800", "4500"],
    "PvE Resist Skill Amp.": ["1%", "2%", "3%", "4%", "5%"],
    "PvE Resist Crit. DMG": ["2%", "4%", "6%", "8%", "10%"]
}

def get_all_skills():
    """Get all available skills"""
    return KNOWN_SKILLS

def get_offensive_skills():
    """Get all offensive skills"""
    return OFFENSIVE_SKILLS

def get_defensive_skills():
    """Get all defensive skills"""
    return DEFENSIVE_SKILLS

def get_stat_variations(stat_name):
    """Get possible variations for a specific stat"""
    return STAT_VARIATIONS.get(stat_name, [])

def get_all_stat_variations():
    """Get all stat variations dictionary"""
    return STAT_VARIATIONS
