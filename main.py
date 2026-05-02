"""Entry point for the Task Scheduler desktop app."""

from pathlib import Path

from task_scheduler.core.services import TaskService
from task_scheduler.core.storage import JsonStorage
from task_scheduler.ui.app import TaskSchedulerApp


def main() -> None:
    """Bootstrap dependencies and launch UI."""

    storage = JsonStorage(Path("data/tasks.json"))
    service = TaskService(storage)
    app = TaskSchedulerApp(service)
    app.mainloop()


if __name__ == "__main__":
    main()
