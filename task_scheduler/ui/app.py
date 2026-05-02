"""Tkinter UI for the task scheduler desktop app.

The interface is intentionally minimal: date selector, task input,
and a list with color-coded status.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from task_scheduler.core.models import TaskStatus
from task_scheduler.core.services import TaskService


class TaskSchedulerApp(tk.Tk):
    """Main window for the to-do scheduler application."""

    STATUS_COLORS = {
        TaskStatus.DONE: "#D4EDDA",  # soft green
        TaskStatus.NOT_DONE: "#F8D7DA",  # soft red
        TaskStatus.ONGOING: "#FFF3CD",  # soft yellow
    }

    def __init__(self, service: TaskService) -> None:
        super().__init__()
        self.service = service
        self.title("Task Scheduler")
        self.geometry("760x500")
        self.minsize(680, 420)

        # Keep current selected date in a StringVar for easy UI data-binding.
        self.current_date_var = tk.StringVar(value=date.today().isoformat())
        self.task_title_var = tk.StringVar()

        self._build_layout()
        self._refresh_day_dropdown()
        self._load_tasks_for_selected_day()

    def _build_layout(self) -> None:
        """Construct all widgets in the window."""

        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(root)
        controls.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(controls, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(controls, textvariable=self.current_date_var, width=16)
        self.date_entry.grid(row=0, column=1, padx=(8, 10), sticky="w")

        self.day_dropdown = ttk.Combobox(controls, width=18, state="readonly")
        self.day_dropdown.grid(row=0, column=2, padx=(0, 10), sticky="w")
        self.day_dropdown.bind("<<ComboboxSelected>>", self._on_day_selected)

        ttk.Button(controls, text="Open / Create Day", command=self._open_or_create_day).grid(
            row=0, column=3, padx=(0, 10)
        )

        add_row = ttk.Frame(root)
        add_row.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(add_row, text="Task:").grid(row=0, column=0, sticky="w")
        ttk.Entry(add_row, textvariable=self.task_title_var, width=45).grid(
            row=0, column=1, padx=(8, 10), sticky="we"
        )

        ttk.Label(add_row, text="Status:").grid(row=0, column=2, sticky="w")
        self.new_task_status = ttk.Combobox(
            add_row, values=[s.value for s in TaskStatus], width=12, state="readonly"
        )
        self.new_task_status.current(1)
        self.new_task_status.grid(row=0, column=3, padx=(8, 10))

        ttk.Button(add_row, text="Add Task", command=self._add_task).grid(row=0, column=4)
        add_row.columnconfigure(1, weight=1)

        # Treeview gives a clean, table-like task view.
        self.tree = ttk.Treeview(root, columns=("task", "status"), show="headings", height=14)
        self.tree.heading("task", text="Task")
        self.tree.heading("status", text="Status")
        self.tree.column("task", width=500, anchor="w")
        self.tree.column("status", width=130, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        for status, color in self.STATUS_COLORS.items():
            self.tree.tag_configure(status.value, background=color)

        status_row = ttk.Frame(root)
        status_row.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_row, text="Change selected task status:").pack(side=tk.LEFT)
        self.update_status_combo = ttk.Combobox(
            status_row, values=[s.value for s in TaskStatus], width=14, state="readonly"
        )
        self.update_status_combo.current(0)
        self.update_status_combo.pack(side=tk.LEFT, padx=(8, 8))
        ttk.Button(status_row, text="Update", command=self._update_selected_task_status).pack(
            side=tk.LEFT
        )

    def _parse_selected_date(self) -> date | None:
        """Parse date input and show user-friendly errors if invalid."""

        text = self.current_date_var.get().strip()
        try:
            return date.fromisoformat(text)
        except ValueError:
            messagebox.showerror("Invalid date", "Please use YYYY-MM-DD format.")
            return None

    def _refresh_day_dropdown(self) -> None:
        """Reload date dropdown from persisted data."""

        days = self.service.list_days()
        self.day_dropdown["values"] = days

    def _open_or_create_day(self) -> None:
        """Open existing or create new page for the entered date."""

        selected_date = self._parse_selected_date()
        if not selected_date:
            return

        self.service.get_or_create_day(selected_date)
        self._refresh_day_dropdown()
        self._load_tasks_for_selected_day()

    def _load_tasks_for_selected_day(self) -> None:
        """Render tasks for currently selected date in tree view."""

        selected_date = self._parse_selected_date()
        if not selected_date:
            return

        day = self.service.get_or_create_day(selected_date)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, task in enumerate(day.tasks):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(task.title, task.status.value),
                tags=(task.status.value,),
            )

    def _on_day_selected(self, _event: tk.Event) -> None:
        """Handle date selection from dropdown."""

        chosen = self.day_dropdown.get()
        if chosen:
            self.current_date_var.set(chosen)
            self._load_tasks_for_selected_day()

    def _add_task(self) -> None:
        """Validate input and add a task for the current date."""

        selected_date = self._parse_selected_date()
        if not selected_date:
            return

        title = self.task_title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing task", "Please enter a task description.")
            return

        status = TaskStatus(self.new_task_status.get())
        self.service.add_task(selected_date, title, status)

        self.task_title_var.set("")
        self._refresh_day_dropdown()
        self._load_tasks_for_selected_day()

    def _update_selected_task_status(self) -> None:
        """Update status for selected row."""

        selected_date = self._parse_selected_date()
        if not selected_date:
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a task first.")
            return

        task_index = int(selected_item[0])
        new_status = TaskStatus(self.update_status_combo.get())
        self.service.update_task_status(selected_date, task_index, new_status)
        self._load_tasks_for_selected_day()
