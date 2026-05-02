"""Business logic for the task scheduler.

The service layer gives the UI a clean, high-level API.
This helps keep UI code small and allows easier future extensions.
"""

from __future__ import annotations

from datetime import date

from .models import AppData, DayTasks, Task, TaskStatus
from .storage import JsonStorage


class TaskService:
    """Provides task operations while handling persistence."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        self.data: AppData = self.storage.load()

    def get_or_create_day(self, task_date: date) -> DayTasks:
        """Return day's task list, creating a new day if needed."""

        key = task_date.isoformat()
        if key not in self.data.days:
            self.data.days[key] = DayTasks(task_date=task_date)
            self.storage.save(self.data)
        return self.data.days[key]

    def list_days(self) -> list[str]:
        """Return existing day keys in ascending date order."""

        return sorted(self.data.days.keys())

    def add_task(self, task_date: date, title: str, status: TaskStatus) -> None:
        """Create and persist a new task for a date."""

        day = self.get_or_create_day(task_date)
        day.tasks.append(Task(title=title, status=status))
        self.storage.save(self.data)

    def update_task_status(self, task_date: date, task_index: int, status: TaskStatus) -> None:
        """Update status for one task and persist changes."""

        day = self.get_or_create_day(task_date)
        if 0 <= task_index < len(day.tasks):
            day.tasks[task_index].status = status
            self.storage.save(self.data)
