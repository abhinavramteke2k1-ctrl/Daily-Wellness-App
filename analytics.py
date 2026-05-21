"""
The Analytics class handles all data analysis
for the wellness journal — weekly summaries,
trend detection, and personalised insights.

Advanced topics demonstrated:
  • OOP with methods and encapsulation
  • List comprehensions
  • datetime arithmetic
  • Correlation detection across data fields
"""

from datetime import datetime, timedelta
from journal_entry import JournalEntry


class Analytics:
    """
    Analyses a list of JournalEntry objects to produce
    summaries and personalised insights.

    Args:
        entries: List of JournalEntry objects to analyse.
    """

    def __init__(self, entries: list[JournalEntry]):
        self._entries = sorted(entries, key=lambda e: e.date)

    # Internal helpers

    def _last_n_days(self, n: int) -> list[JournalEntry]:
        """Return entries from the last n days."""
        cutoff = (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")
        return [e for e in self._entries if e.date >= cutoff]

    @staticmethod
    def _average(values: list[float]) -> float:
        """Return the mean of a list, or 0.0 if empty."""
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _pearson_sign(xs: list[float], ys: list[float]) -> float:
        """
        Return the sign of the Pearson correlation between two lists.
        Positive → tend to rise together; Negative → inverse relationship.
        Returns 0 if insufficient data.
        """
        n = len(xs)
        if n < 3:
            return 0.0
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        numerator   = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        denom_x     = sum((x - mean_x) ** 2 for x in xs) ** 0.5
        denom_y     = sum((y - mean_y) ** 2 for y in ys) ** 0.5
        if denom_x == 0 or denom_y == 0:
            return 0.0
        return numerator / (denom_x * denom_y)

    # Public API

    def weekly_summary(self) -> dict:
        """
        Compute summary statistics for the last 7 days.

        Returns:
            Dictionary with count, averages, best day, and most-sleep day.
        """
        week = self._last_n_days(7)
        if not week:
            return {}

        avg_mood   = self._average([e.mood   for e in week])
        avg_energy = self._average([e.energy for e in week])
        avg_sleep  = self._average([e.sleep  for e in week])

        best_entry      = max(week, key=lambda e: e.mood + e.energy)
        most_sleep_entry = max(week, key=lambda e: e.sleep)

        best_day      = datetime.strptime(best_entry.date, "%Y-%m-%d").strftime("%A, %d %b")
        most_sleep_day = datetime.strptime(most_sleep_entry.date, "%Y-%m-%d").strftime("%A, %d %b")

        return {
            "count":          len(week),
            "avg_mood":       avg_mood,
            "avg_energy":     avg_energy,
            "avg_sleep":      avg_sleep,
            "best_day":       best_day,
            "most_sleep_day": most_sleep_day,
            "most_sleep":     most_sleep_entry.sleep,
        }

    def generate_insights(self) -> list[str]:
        """
        Analyse entry data and return a list of personalised insight strings.

        Checks for correlations between sleep & mood, sleep & energy,
        mood & energy, and overall trends over recent weeks.

        Returns:
            List of human-readable insight strings.
        """
        insights = []
        all_e    = self._entries

        # Need at least 3 entries for meaningful analysis
        if len(all_e) < 2:
            return ["Keep logging — more entries unlock richer insights!"]

        moods    = [e.mood   for e in all_e]
        energies = [e.energy for e in all_e]
        sleeps   = [e.sleep  for e in all_e]

        # Sleep - Mood correlation
        r_sleep_mood = self._pearson_sign(sleeps, moods)
        if r_sleep_mood > 0.3:
            insights.append(
                "😴💛 You tend to feel happier on days after more sleep. "
                "Prioritising rest seems to lift your mood."
            )
        elif r_sleep_mood < -0.3:
            insights.append(
                "🤔 Interestingly, your mood doesn't clearly improve with more sleep. "
                "Other factors might be influencing how you feel."
            )

        #  Sleep - Energy correlation
        r_sleep_energy = self._pearson_sign(sleeps, energies)
        if r_sleep_energy > 0.3:
            insights.append(
                "⚡ More sleep is linked to higher energy for you. "
                "Aim for a consistent bedtime to keep your energy up."
            )

        #  Mood - Energy correlation
        r_mood_energy = self._pearson_sign(moods, energies)
        if r_mood_energy > 0.4:
            insights.append(
                "🌟 Your mood and energy tend to rise and fall together — "
                "when one improves, so does the other."
            )

        #  Average sleep insight
        avg_sleep = self._average(sleeps)
        if avg_sleep < 6:
            insights.append(
                f"🛌 Your average sleep is {avg_sleep:.1f} hrs — below the recommended 7–9. "
                "Even small improvements in sleep can make a big difference."
            )
        elif avg_sleep >= 8:
            insights.append(
                f"✅ You're averaging {avg_sleep:.1f} hrs of sleep — great work maintaining healthy rest!"
            )

        # Mood trend (comparing first half vs second half)
        mid = len(all_e) // 2
        first_half_mood  = self._average([e.mood for e in all_e[:mid]])
        second_half_mood = self._average([e.mood for e in all_e[mid:]])
        diff = second_half_mood - first_half_mood

        if diff >= 0.5:
            insights.append(
                f"📈 Your mood has been trending upward recently — you're doing better than before. Keep it up!"
            )
        elif diff <= -0.5:
            insights.append(
                "📉 Your mood has dipped a little compared to earlier entries. "
                "Be kind to yourself — it's okay to have harder periods."
            )

        # Low energy days pattern
        low_energy_days = [e for e in all_e if e.energy <= 2]
        if len(low_energy_days) >= 3:
            avg_sleep_on_low = self._average([e.sleep for e in low_energy_days])
            insights.append(
                f"🔋 On your lowest-energy days, you averaged {avg_sleep_on_low:.1f} hrs of sleep. "
                "Consider whether fatigue is playing a role."
            )

        # Consistency encouragement
        if len(all_e) >= 7:
            insights.append(
                f"🏅 You've logged {len(all_e)} entries so far — consistency is the foundation of self-awareness!"
            )

        return insights if insights else ["Keep logging more entries to unlock personalised insights!"]
