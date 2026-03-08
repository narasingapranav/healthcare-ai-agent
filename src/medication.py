from datetime import datetime


def upcoming_reminders(medications: list, window_minutes: int = 60) -> list[str]:
    now = datetime.now()
    reminders: list[str] = []

    for medication in medications:
        schedule = medication["schedule_time"]
        try:
            scheduled_time = datetime.strptime(schedule, "%H:%M")
        except ValueError:
            continue

        due = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, second=0, microsecond=0)
        delta_minutes = (due - now).total_seconds() / 60

        if 0 <= delta_minutes <= window_minutes:
            reminders.append(
                f"Take {medication['name']} ({medication['dosage']}) at {medication['schedule_time']}"
            )

    return reminders
