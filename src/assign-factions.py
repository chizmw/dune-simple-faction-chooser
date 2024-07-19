import csv
import pandas as pd
from collections import defaultdict

# Read preferences from CSV
preferences = pd.read_csv("preferences.csv")

# Initialize available factions and assignment dict
factions = [
    "Bene Gesserit",
    "Choam",
    "Emperor",
    "Fremen",
    "Harkonnen",
    "Ixian",
    "Richese",
    "Spacing Guild",
    "Tleilaxu",
    "Atreides",
]
assignments = {player: None for player in preferences["name"]}

# Priority dictionary
priority = defaultdict(list)
for index, row in preferences.iterrows():
    for i in range(1, 5):
        priority[row[f"choice {i}"]].append((row["name"], i))

# Sort priority by preference level (lower number means higher priority)
sorted_priority = sorted(
    priority.items(), key=lambda item: (len(item[1]), min(pref[1] for pref in item[1]))
)

print("Sorted Priority:")
for faction, prefs in sorted_priority:
    print(f"{faction}: {prefs}")

# Assign factions based on sorted priority
assigned_factions = set()
for faction, prefs in sorted_priority:
    print("Faction: " + faction)
    for player, priority_level in sorted(prefs, key=lambda x: x[1]):
        if assignments[player] is None and faction not in assigned_factions:
            assignments[player] = faction
            assigned_factions.add(faction)
            break

# Print the final assignments
print("Final Assignments:")
for player, faction in assignments.items():
    print(f"{player}: {faction}")
