"""Persistence layer for storing and loading task data as JSON.

The storage interface is intentionally isolated from UI and business logic.
This separation keeps the project maintainable and makes it straightforward
for future upgrades (for example: SQLite, cloud sync, API-backed storage).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict

from .models import AppData, DayTasks, Task, TaskStatus


class JsonStorage:
    """Simple JSON file-backed storage.

    Attributes:
        file_path: The JSON file used for persistence.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def load(self) -> AppData:
        """Load app data from disk.

        Returns:
            An ``AppData`` instance. If the file does not exist or is invalid,
            a fresh empty dataset is returned.
        """

        if not self.file_path.exists():
            return AppData()

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # Gracefully recover by returning empty data.
            return AppData()

        days: Dict[str, DayTasks] = {}
        for date_key, payload in raw.get("days", {}).items():
            day_tasks = DayTasks(task_date=date.fromisoformat(date_key), tasks=[])
            for task_payload in payload.get("tasks", []):
                status_text = task_payload.get("status", TaskStatus.NOT_DONE.value)
                # Fallback to NOT_DONE if an unexpected status was written.
                try:
                    status = TaskStatus(status_text)
                except ValueError:
                    status = TaskStatus.NOT_DONE

                day_tasks.tasks.append(
                    Task(title=task_payload.get("title", ""), status=status)
                )
            days[date_key] = day_tasks

        return AppData(days=days)

    def save(self, data: AppData) -> None:
        """Persist app data to disk.

        The JSON output is pretty-printed to keep the save file human-readable.
        """

        # Ensure parent folder exists so first-time app runs are smooth.
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        serializable = {
            "days": {
                date_key: {
                    "task_date": day.task_date.isoformat(),
                    "tasks": [
                        {
                            "title": task.title,
                            "status": task.status.value,
                        }
                        for task in day.tasks
                    ],
                }
                for date_key, day in data.days.items()
            }
        }

        self.file_path.write_text(
            json.dumps(serializable, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
