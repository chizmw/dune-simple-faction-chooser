import pandas as pd
import random
from typing import Any, List, Dict, Set
from rich.console import Console  # type: ignore
from rich.markdown import Markdown


console = Console()


def print_markdown(markdown: str) -> None:
    console.print(Markdown(markdown))


# Known faction names
base_factions: List[str] = [
    "Bene Gesserit",
    "Emperor",
    "Fremen",
    "Harkonnen",
    "Spacing Guild",
    "Atreides",
]
expansion_factions: List[str] = ["Choam", "Richese", "Ixian", "Tleilaxu"]
all_factions: Set[str] = set(base_factions + expansion_factions)

# Read preferences from CSV
preferences: pd.DataFrame = pd.read_csv("preferences.csv")

# abort immediately if we have more than 6 players
if len(preferences) > 6:
    raise ValueError("Too many players")


CHOICE_1: str = "choice 1"
CHOICE_2: str = "choice 2"
CHOICE_3: str = "choice 3"
CHOICE_4: str = "choice 4"


# Ensure faction names in preferences match known factions (case insensitive)
def validate_factions(preferences: pd.DataFrame, all_factions: Set[str]) -> None:
    valid_factions = [f.lower() for f in all_factions]
    for column in [CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4]:
        # Exclude 'noprefs' from validation
        preferences[column] = preferences[column].fillna("").astype(str).str.lower()

        # loop through the column and find invalid faction names
        # we can throw an error immediately
        for index, row in preferences.iterrows():
            if (
                row[column] != "noprefs"
                and row[column] != ""
                and row[column] not in valid_factions
            ):
                raise ValueError(
                    f"Invalid faction name '{row[column]}' found in column '{column}'"
                )


validate_factions(preferences, all_factions)

# Initialize assignments dict
assignments: Dict[str, Any] = {player: None for player in preferences["name"]}
available_factions: Set[str] = set(base_factions)


# Function to assign factions based on preference level with random selection
def assign_factions(
    preferences: pd.DataFrame,
    assignments: Dict[str, Any],
    available_factions: Set[str],
    choice_level: str,
) -> None:
    choices_dict: Dict[str, List[str]] = {}
    for index, row in preferences.iterrows():
        if assignments[row["name"]] is None:
            faction: Optional[str] = row[choice_level]
            faction_lower = faction.lower() if isinstance(faction, str) else ""
            if faction_lower in [
                f.lower() for f in available_factions
            ] or faction_lower in [f.lower() for f in expansion_factions]:
                faction = next(
                    (f for f in all_factions if f.lower() == faction_lower), None
                )
                if faction:
                    if faction not in choices_dict:
                        choices_dict[faction] = []
                    choices_dict[faction].append(row["name"])
                    # If the faction is an expansion faction, add it to available_factions
                    if faction in expansion_factions:
                        available_factions.add(faction)

    for faction, players in choices_dict.items():
        if len(players) == 1:
            # Only one player wants this faction
            player: str = players[0]
            assignments[player] = faction
            available_factions.remove(faction)
        else:
            # Multiple players want this faction, choose one randomly
            chosen_player: str = random.choice(players)
            assignments[chosen_player] = faction
            available_factions.remove(faction)
            # Remove chosen player from the list
            players.remove(chosen_player)
            # Add remaining players back to the dataframe with their choice removed
            for player in players:
                preferences.loc[preferences["name"] == player, choice_level] = "None"


# Separate players with preferences from those without
players_with_prefs: pd.DataFrame = preferences[
    preferences[CHOICE_1] != "noprefs"
].copy()
players_without_prefs: pd.DataFrame = preferences[
    preferences[CHOICE_1] == "noprefs"
].copy()

# Limit to 6 players with preferences
players_with_prefs = players_with_prefs.head(6)
players_without_prefs = players_without_prefs.head(6 - len(players_with_prefs))

# Assign factions based on each choice level for players with preferences
for choice_level in [CHOICE_1, CHOICE_2, CHOICE_3, CHOICE_4]:
    assign_factions(players_with_prefs, assignments, available_factions, choice_level)

# Assign remaining factions to players without preferences and update existing assignments
remaining_factions: List[str] = list(available_factions)
random.shuffle(remaining_factions)
for index, row in players_without_prefs.iterrows():
    player: str = row["name"]
    if remaining_factions:
        if assignments.get(player) is not None:
            # If the player already has an assignment (should not happen, but just in case)
            continue
        assignments[player + "®"] = remaining_factions.pop(0)
        # remove "player" from assignments
        assignments.pop(player)

# we'll build up a markdown string and then use "print_markdown" to print it
markdown: str = ""

# the header
markdown += "**<u>Faction Assignments</u>**\n\n"

# Print the final assignments
# sort by player name
assignments = dict(sorted(assignments.items()))
for player, faction in assignments.items():
    # add a line to the markdown string
    markdown += f"- {player}: {faction}\n"

print_markdown(markdown)
