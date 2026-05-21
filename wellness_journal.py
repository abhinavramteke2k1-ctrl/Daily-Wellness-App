"""
Description:
A command-line wellness journal that lets users log 
their daily mood, energy, sleep, and notes.
Tracks trends over time and provides personalised insights.
"""

import os
import json
from datetime import datetime, timedelta
from journal_entry import JournalEntry
from analytics import Analytics


#  Constants

DATA_FILE = "journal_data.json"
APP_NAME  = "Daily Wellness Journal"
DIVIDER   = "─" * 50



#  File I/O helpers

def load_entries() -> list[JournalEntry]:
    """Load all journal entries from the JSON data file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [JournalEntry.from_dict(d) for d in raw]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Warning: Could not read data file ({e}). Starting fresh.")
        return []


def save_entries(entries: list[JournalEntry]) -> None:
    """Save all journal entries to the JSON data file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


#  Input helpers

def get_int_input(prompt: str, lo: int, hi: int) -> int:
    """Prompt the user for an integer within [lo, hi], re-asking on invalid input."""
    while True:
        try:
            value = int(input(prompt).strip())
            if lo <= value <= hi:
                return value
            print(f"  Please enter a number between {lo} and {hi}.")
        except ValueError:
            print("  Invalid input — please enter a whole number.")


def get_float_input(prompt: str, lo: float, hi: float) -> float:
    """Prompt the user for a float within [lo, hi]."""
    while True:
        try:
            value = float(input(prompt).strip())
            if lo <= value <= hi:
                return value
            print(f"  Please enter a value between {lo} and {hi}.")
        except ValueError:
            print("  Invalid input — please enter a number (e.g. 7.5).")



#  Menu actions

def log_today(entries: list[JournalEntry]) -> list[JournalEntry]:
    """Guide the user through logging today's entry."""
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Prevent duplicate entries for the same day
    for e in entries:
        if e.date == today_str:
            print(f"\n  You already have an entry for today ({today_str}).")
            overwrite = input("  Overwrite it? (y/n): ").strip().lower()
            if overwrite != "y":
                return entries
            entries = [e for e in entries if e.date != today_str]
            break

    print(f"\n  {DIVIDER}")
    print("  📝  New Entry —", datetime.now().strftime("%A, %d %B %Y"))
    print(f"  {DIVIDER}")

    mood   = get_int_input("  Mood (1 = terrible → 5 = amazing): ", 1, 5)
    energy = get_int_input("  Energy level (1 = drained → 5 = energised): ", 1, 5)
    sleep  = get_float_input("  Hours of sleep last night (0–24): ", 0, 24)
    print("  Daily note (press Enter to skip):")
    note   = input("  > ").strip()

    entry = JournalEntry(
        date=today_str,
        mood=mood,
        energy=energy,
        sleep=sleep,
        note=note
    )
    entries.append(entry)
    save_entries(entries)

    print(f"\n  ✅  Entry saved! Great job checking in today.")
    return entries


def view_recent(entries: list[JournalEntry]) -> None:
    """Display the last 7 entries in a readable format."""
    if not entries:
        print("\n  No entries yet. Start logging to see your history!")
        return

    recent = sorted(entries, key=lambda e: e.date, reverse=True)[:7]
    print(f"\n  {DIVIDER}")
    print("  📖  Recent Entries (last 7 days)")
    print(f"  {DIVIDER}")

    mood_labels   = {1: "😞 Terrible", 2: "😕 Poor", 3: "😐 Okay", 4: "🙂 Good", 5: "😄 Amazing"}
    energy_labels = {1: "💤 Drained", 2: "😴 Low", 3: "😐 Moderate", 4: "⚡ Energised", 5: "🔥 Pumped"}

    for e in recent:
        dt = datetime.strptime(e.date, "%Y-%m-%d").strftime("%a, %d %b %Y")
        print(f"\n  {dt}")
        print(f"    Mood:   {mood_labels.get(e.mood, e.mood)}")
        print(f"    Energy: {energy_labels.get(e.energy, e.energy)}")
        print(f"    Sleep:  {e.sleep:.1f} hrs")
        if e.note:
            print(f"    Note:   \"{e.note}\"")


def show_weekly_summary(entries: list[JournalEntry]) -> None:
    """Show averages and trends for the past 7 days."""
    if len(entries) < 2:
        print("\n  Not enough entries for a summary yet. Log a few more days!")
        return

    analytics = Analytics(entries)
    summary   = analytics.weekly_summary()

    print(f"\n  {DIVIDER}")
    print("  📊  Weekly Summary (last 7 days)")
    print(f"  {DIVIDER}")
    print(f"  Entries logged:   {summary['count']} day(s)")
    print(f"  Avg mood:         {summary['avg_mood']:.1f} / 5")
    print(f"  Avg energy:       {summary['avg_energy']:.1f} / 5")
    print(f"  Avg sleep:        {summary['avg_sleep']:.1f} hrs")
    print(f"  Best day:         {summary['best_day']}")
    print(f"  Most sleep:       {summary['most_sleep_day']} ({summary['most_sleep']:.1f} hrs)")


def show_insights(entries: list[JournalEntry]) -> None:
    """Display personalised insights based on logged data."""
    if len(entries) < 2:
        print("\n  Log at least 2 entries to unlock personalised insights!")
        return

    analytics = Analytics(entries)
    insights  = analytics.generate_insights()

    print(f"\n  {DIVIDER}")
    print("  💡  Personalised Insights")
    print(f"  {DIVIDER}")
    for insight in insights:
        print(f"  • {insight}")


def show_streak(entries: list[JournalEntry]) -> None:
    """Calculate and display the user's current logging streak."""
    if not entries:
        print("\n  No entries yet — start your streak today!")
        return

    dates  = sorted({e.date for e in entries}, reverse=True)
    streak = 1
    today  = datetime.now().strftime("%Y-%m-%d")

    # If the most recent entry isn't today or yesterday, streak is 0
    if dates[0] < (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
        print("\n  🔴  Your streak is 0 days. Log today to start again!")
        return

    for i in range(1, len(dates)):
        expected = (datetime.strptime(dates[i - 1], "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        if dates[i] == expected:
            streak += 1
        else:
            break

    emoji = "🔥" if streak >= 7 else "✨" if streak >= 3 else "⭐"
    print(f"\n  {emoji}  Current streak: {streak} day(s) in a row!")
    if streak >= 7:
        print("  Amazing consistency — keep it up!")
    elif streak >= 3:
        print("  Great work! You're building a solid habit.")
    else:
        print("  Every day counts — come back tomorrow!")


#  Main menu

def print_menu() -> None:
    print(f"\n  {DIVIDER}")
    print(f"  🌿  {APP_NAME}")
    print(f"  {DIVIDER}")
    print("  1.  Log today's entry")
    print("  2.  View recent entries")
    print("  3.  Weekly summary")
    print("  4.  Personalised insights")
    print("  5.  Check my streak")
    print("  6.  Exit")
    print(f"  {DIVIDER}")


def main() -> None:
    """Main program loop."""
    print(f"\n  Welcome to the {APP_NAME}!")
    print("  Your daily check-in for a healthier mind. 🌱")

    entries = load_entries()

    menu_actions = {
        "1": lambda: log_today(entries),
        "2": lambda: view_recent(entries),
        "3": lambda: show_weekly_summary(entries),
        "4": lambda: show_insights(entries),
        "5": lambda: show_streak(entries),
    }

    while True:
        print_menu()
        choice = input("  Choose an option (1-6): ").strip()

        if choice == "6":
            print("\n  Take care of yourself. See you tomorrow! 🌙\n")
            break
        elif choice in menu_actions:
            result = menu_actions[choice]()
            # log_today returns updated entries list
            if choice == "1" and result is not None:
                entries = result
        else:
            print("  Invalid choice — please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()