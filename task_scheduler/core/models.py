"""Domain models for the task scheduler application.

This module intentionally contains only data-centric definitions.
Keeping UI logic out of these classes makes them reusable and easy to test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List


class TaskStatus(str, Enum):
    """Supported status values for a task.

    Inheriting from ``str`` helps with JSON serialization while still
    providing type safety through an enum.
    """

    DONE = "Done"
    NOT_DONE = "Not Done"
    ONGOING = "On-going"


@dataclass
class Task:
    """Single to-do item for a specific day."""

    title: str
    status: TaskStatus = TaskStatus.NOT_DONE


@dataclass
class DayTasks:
    """Collection of tasks for one date."""

    task_date: date
    tasks: List[Task] = field(default_factory=list)


@dataclass
class AppData:
    """Top-level structure used by storage.

    The keys are ISO date strings (YYYY-MM-DD) and values are all tasks
    registered for that day.
    """

    days: Dict[str, DayTasks] = field(default_factory=dict)
