"""
Project FRIDAY
Daily Briefing
"""

from datetime import date

from modules.habits import habit_tracker
from modules.routine import routine


class DailyBriefing:

    # ========================================
    # MORNING BRIEFING
    # ========================================

    def get(self):

        # ----------------------------------------
        # Load habits
        # ----------------------------------------

        habits = habit_tracker.load()

        today = date.today().isoformat()

        total_habits = len(habits)

        completed_habits = 0

        active_streaks = []

        for name, habit in habits.items():

            if habit.get(
                "last_completed"
            ) == today:

                completed_habits += 1

            streak = habit.get(
                "streak",
                0
            )

            if streak > 0:

                active_streaks.append(
                    (name, streak)
                )

        # ----------------------------------------
        # Load routine
        # ----------------------------------------

        routine_data = routine.load()

        morning = routine_data.get(
            "morning",
            []
        )

        evening = routine_data.get(
            "evening",
            []
        )

        # ----------------------------------------
        # Build briefing
        # ----------------------------------------

        parts = []

        parts.append(
            "Good morning, Sir."
        )

        # ----------------------------------------
        # Habits
        # ----------------------------------------

        if total_habits:

            parts.append(
                f"You have {total_habits} habits today."
            )

            parts.append(
                f"You have completed "
                f"{completed_habits} of them so far."
            )

        else:

            parts.append(
                "You don't have any habits yet."
            )

        # ----------------------------------------
        # Morning routine
        # ----------------------------------------

        if morning:

            parts.append(
                f"Your morning routine has "
                f"{len(morning)} tasks."
            )

        else:

            parts.append(
                "Your morning routine is empty."
            )

        # ----------------------------------------
        # Evening routine
        # ----------------------------------------

        if evening:

            parts.append(
                f"Your evening routine has "
                f"{len(evening)} tasks."
            )

        # ----------------------------------------
        # Best active streak
        # ----------------------------------------

        if active_streaks:

            best_habit, best_streak = max(
                active_streaks,
                key=lambda item: item[1]
            )

            parts.append(
                f"Your strongest current streak "
                f"is {best_streak} days for "
                f"{best_habit}."
            )

        return " ".join(parts)

    # ========================================
    # TODAY'S PLAN
    # ========================================

    def today_plan(self):

        habits = habit_tracker.load()

        routine_data = routine.load()

        morning = routine_data.get(
            "morning",
            []
        )

        evening = routine_data.get(
            "evening",
            []
        )

        today = date.today().isoformat()

        lines = []

        lines.append(
            "Here's your plan for today, Sir:"
        )

        # ----------------------------------------
        # Morning routine
        # ----------------------------------------

        if morning:

            lines.append(
                "\n🌅 Morning routine:"
            )

            for task in morning:

                lines.append(
                    f"• {task}"
                )

        # ----------------------------------------
        # Habits
        # ----------------------------------------

        if habits:

            lines.append(
                "\n📅 Habits:"
            )

            for name, habit in habits.items():

                if habit.get(
                    "last_completed"
                ) == today:

                    status = "✅"

                else:

                    status = "⬜"

                lines.append(
                    f"{status} {name}"
                )

        # ----------------------------------------
        # Evening routine
        # ----------------------------------------

        if evening:

            lines.append(
                "\n🌙 Evening routine:"
            )

            for task in evening:

                lines.append(
                    f"• {task}"
                )

        # ----------------------------------------
        # Nothing scheduled
        # ----------------------------------------

        if (
            not morning
            and not habits
            and not evening
        ):

            lines.append(
                "\nYour day is completely free."
            )

        return "\n".join(lines)

    # ========================================
    # DAILY PROGRESS
    # ========================================

    def progress(self):

        habits = habit_tracker.load()

        today = date.today().isoformat()

        total = len(habits)

        completed = 0

        best_habit = None

        best_streak = 0

        # ----------------------------------------
        # No habits
        # ----------------------------------------

        if total == 0:

            return (
                "You don't have any habits yet, Sir."
            )

        # ----------------------------------------
        # Calculate progress
        # ----------------------------------------

        for name, habit in habits.items():

            # Completed today

            if habit.get(
                "last_completed"
            ) == today:

                completed += 1

            # Strongest streak

            streak = habit.get(
                "streak",
                0
            )

            if streak > best_streak:

                best_streak = streak

                best_habit = name

        # ----------------------------------------
        # Percentage
        # ----------------------------------------

        percentage = round(
            (completed / total) * 100
        )

        # ----------------------------------------
        # Response
        # ----------------------------------------

        response = (
            f"Sir, you've completed "
            f"{completed} of {total} habits today, "
            f"which is {percentage}%."
        )

        # ----------------------------------------
        # Best streak
        # ----------------------------------------

        if (
            best_habit
            and best_streak > 0
        ):

            response += (
                f" Your strongest streak is "
                f"{best_streak} days for "
                f"{best_habit}."
            )

        # ----------------------------------------
        # Fully completed
        # ----------------------------------------

        if completed == total:

            response += (
                " Excellent work, Sir. "
                "You've completed every habit today."
            )

        # ----------------------------------------
        # Nothing completed
        # ----------------------------------------

        elif completed == 0:

            response += (
                " You haven't completed any "
                "habits yet today."
            )

        return response


briefing = DailyBriefing()