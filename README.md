# Task-Scheduler

A clean and simple Python desktop to-do scheduler app with:
- **Date-wise pages** (create/open any date)
- **Task statuses**: Done, Not Done, On-going
- **Color coding** by status
- **Persistent storage** in JSON so lists are saved
- **Extensible architecture** (separate models, services, storage, and UI)

## Run

```bash
python main.py
```

> Requires Python 3.10+ (for modern typing syntax).

## Project Structure

- `main.py` → App entrypoint and dependency wiring
- `task_scheduler/core/models.py` → Data models and enums
- `task_scheduler/core/storage.py` → JSON persistence layer
- `task_scheduler/core/services.py` → Business logic service layer
- `task_scheduler/ui/app.py` → Tkinter desktop UI
- `data/tasks.json` → Saved tasks (created automatically on first save)

This design makes it easy to add future features such as:
- delete/edit task
- search/filter
- priorities and tags
- reminders
- export/import
- alternate storage backend (SQLite/API)
