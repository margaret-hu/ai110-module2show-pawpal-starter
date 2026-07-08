import re
from dataclasses import dataclass, field
from datetime import date as Date, datetime, timedelta

_AVAILABILITY_RE = re.compile(
    r"(?:(?P<hours>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours))?"
    r"\s*(?:(?P<minutes>\d+)\s*(?:m|min|mins|minute|minutes))?",
    re.IGNORECASE,
)

PRIORITY_VALUES = {"low": 1, "medium": 2, "high": 3}
RECURRENCE_VALUES = {"daily", "weekly"}
_RECURRENCE_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    type: str
    status: str = "incomplete"
    time: str | None = None
    recurrence: str | None = None
    due_date: Date | None = None

    def mark_complete(self) -> "Task | None":
        """Mark this task's status as complete, returning a fresh instance for its next occurrence if it recurs."""
        self.status = "complete"
        return self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Return a new incomplete Task for this task's next occurrence, or None if it doesn't recur."""
        if self.recurrence not in RECURRENCE_VALUES:
            return None
        next_due_date = self.due_date + _RECURRENCE_DELTAS[self.recurrence] if self.due_date else None
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            type=self.type,
            time=self.time,
            recurrence=self.recurrence,
            due_date=next_due_date,
        )

    def updateTask(
        self,
        name: str | None = None,
        duration: int | None = None,
        priority: str | None = None,
        type: str | None = None,
        time: str | None = None,
        recurrence: str | None = None,
        due_date: Date | None = None,
    ) -> None:
        """Update the given fields of this task, leaving unspecified ones unchanged."""
        if name is not None:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if type is not None:
            self.type = type
        if time is not None:
            self.time = time
        if recurrence is not None:
            self.recurrence = recurrence
        if due_date is not None:
            self.due_date = due_date


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def addTask(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark the given task complete, automatically adding its next occurrence if it recurs."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.addTask(next_task)
        return next_task


@dataclass
class Owner:
    name: str
    availability: str
    pets: list[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def updateInfo(self, name: str | None = None, availability: str | None = None) -> None:
        """Update the given fields of this owner, leaving unspecified ones unchanged."""
        if name is not None:
            self.name = name
        if availability is not None:
            self.availability = availability

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks(self, status: str | None = None, pet_name: str | None = None) -> list[Task]:
        """Return tasks across this owner's pets, optionally filtered by status and/or pet name."""
        pets = self.pets if pet_name is None else [pet for pet in self.pets if pet.name == pet_name]
        tasks = [task for pet in pets for task in pet.tasks]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return tasks

    def available_minutes(self) -> int:
        """Parse this owner's availability string into a number of minutes."""
        text = self.availability.strip().lower()
        if not text:
            return 0

        if ":" in text:
            hours_str, _, minutes_str = text.partition(":")
            if hours_str.strip().isdigit() and minutes_str.strip().isdigit():
                return int(hours_str) * 60 + int(minutes_str)

        match = _AVAILABILITY_RE.fullmatch(text)
        if match and (match.group("hours") or match.group("minutes")):
            hours = float(match.group("hours") or 0)
            minutes = int(match.group("minutes") or 0)
            return int(hours * 60) + minutes

        digits = re.sub(r"[^\d.]", "", text)
        return int(float(digits)) if digits else 0


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    reasoning: str


@dataclass
class Plan:
    pet: Pet
    date: Date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)

    def display(self) -> str:
        """Render this plan's scheduled tasks as a human-readable itinerary."""
        lines = [f"Daily plan for {self.pet.name} ({self.pet.breed}) — {self.date.isoformat()}:"]
        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled.")
        for scheduled in self.scheduled_tasks:
            lines.append(
                f"  {scheduled.start_time} — {scheduled.task.name} "
                f"({scheduled.task.duration} min) [priority: {scheduled.task.priority}]"
            )
        return "\n".join(lines)

    def explain(self) -> str:
        """Render the reasoning behind each scheduled task's placement in this plan."""
        if not self.scheduled_tasks:
            return f"No tasks were scheduled for {self.pet.name} on {self.date.isoformat()}."
        lines = [f"Reasoning for {self.pet.name}'s plan on {self.date.isoformat()}:"]
        for scheduled in self.scheduled_tasks:
            lines.append(f"  - {scheduled.task.name}: {scheduled.reasoning}")
        return "\n".join(lines)


@dataclass
class Scheduler:
    available_minutes: int
    remaining_minutes: int = field(init=False)
    scheduled: list[tuple[Date, Pet, ScheduledTask]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.remaining_minutes = self.available_minutes

    def build_plan(self, pet: Pet, date: Date) -> Plan:
        """Build a time-ordered plan for the given pet and date, prioritizing higher-priority tasks.

        Consumes from this scheduler's shared remaining_minutes pool, so calling this
        for multiple pets in a row correctly splits one owner's time budget between them
        instead of granting each pet the full available_minutes independently. Also checks
        this date's already-scheduled tasks (this pet's or another's) and pushes a task's
        start time forward past any that would otherwise overlap, so build_plan never
        creates a conflict in the first place.
        """
        # select first (knapsack over the whole task list), then order the picked
        # tasks for the day — selection doesn't depend on input order, display does
        selected = self.filter_by_time(pet.tasks)
        ordered = self.sort_by_priority(selected)

        scheduled_tasks = []
        current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=8)
        busy = [self._interval(sched_date, scheduled) for sched_date, _, scheduled in self.scheduled if sched_date == date]
        for rank, task in enumerate(ordered, start=1):
            current_time = self._next_free_start(current_time, task.duration, busy)
            reasoning = (
                f"Ranked #{rank} by priority ({task.priority}) and chosen by the time-budget "
                f"optimizer to make the best use of the {self.remaining_minutes} minute(s) "
                f"remaining today."
            )
            scheduled = ScheduledTask(
                task=task,
                start_time=current_time.strftime("%H:%M"),
                reasoning=reasoning,
            )
            scheduled_tasks.append(scheduled)
            self.scheduled.append((date, pet, scheduled))
            busy.append((current_time, current_time + timedelta(minutes=task.duration)))
            current_time += timedelta(minutes=task.duration)
            self.remaining_minutes -= task.duration

        return Plan(pet=pet, date=date, scheduled_tasks=scheduled_tasks)

    @staticmethod
    def _interval(date: Date, scheduled: ScheduledTask) -> tuple[datetime, datetime]:
        """Return the (start, end) datetime window a scheduled task occupies on the given date."""
        start = datetime.combine(date, datetime.strptime(scheduled.start_time, "%H:%M").time())
        return start, start + timedelta(minutes=scheduled.task.duration)

    @staticmethod
    def _next_free_start(start: datetime, duration: int, busy: list[tuple[datetime, datetime]]) -> datetime:
        """Return the earliest time >= start whose duration-minute window avoids every interval in busy.

        Assumes busy intervals are non-overlapping (guaranteed since this method is what
        keeps them that way), so a single sweep in start order suffices instead of
        restarting the scan from the top each time start is pushed forward.
        """
        for busy_start, busy_end in sorted(busy):
            if start < busy_end and busy_start < start + timedelta(minutes=duration):
                start = busy_end
        return start

    def find_conflicts(self) -> list[tuple[Pet, ScheduledTask, Pet, ScheduledTask]]:
        """Return pairs of scheduled tasks whose time windows overlap on the same date.

        Compares every task this scheduler has placed via build_plan — for the same pet
        or across different pets — since two overlapping windows are a real conflict for
        an owner either way (they can't be in two places, or attending two pets, at once).
        Grouped by date first so tasks on different dates, which can never conflict,
        aren't compared at all.
        """
        by_date: dict[Date, list[tuple[Pet, ScheduledTask]]] = {}
        for date, pet, scheduled in self.scheduled:
            by_date.setdefault(date, []).append((pet, scheduled))

        conflicts = []
        for date, entries in by_date.items():
            for i, (pet_a, sched_a) in enumerate(entries):
                start_a, end_a = self._interval(date, sched_a)
                for pet_b, sched_b in entries[i + 1 :]:
                    start_b, end_b = self._interval(date, sched_b)
                    if start_a < end_b and start_b < end_a:
                        conflicts.append((pet_a, sched_a, pet_b, sched_b))
        return conflicts

    def conflict_warning(self) -> str | None:
        """Return a human-readable warning if any scheduled tasks overlap, or None if there's no conflict.

        Lightweight safety net for callers (e.g. the UI) to surface accidental conflicts —
        such as ones introduced by manually editing a Task's time after it was scheduled —
        without raising, so the program can keep running and just display the warning.
        """
        conflicts = self.find_conflicts()
        if not conflicts:
            return None
        lines = ["Warning: scheduling conflicts detected:"]
        for pet_a, sched_a, pet_b, sched_b in conflicts:
            lines.append(
                f"  - {pet_a.name}'s '{sched_a.task.name}' at {sched_a.start_time} overlaps "
                f"{pet_b.name}'s '{sched_b.task.name}' at {sched_b.start_time}"
            )
        return "\n".join(lines)

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Select the subset of tasks that maximizes total priority value within the remaining minutes.

        Uses 0/1 knapsack (duration = weight, priority = value) instead of a greedy pass, so a
        few lower-priority tasks that fit together aren't crowded out by one long high-priority
        task that alone would consume the whole budget. Ties in total priority value are broken
        in favor of using less total time, which in practice favors fitting more/shorter tasks.
        """
        capacity = self.remaining_minutes
        if capacity <= 0 or not tasks:
            return []

        total_duration = sum(task.duration for task in tasks)
        scores = [
            PRIORITY_VALUES[task.priority] * (total_duration + 1) - task.duration
            for task in tasks
        ]

        # best[w] = highest score achievable within capacity w using tasks considered so far
        best = [[0] * (capacity + 1) for _ in range(len(tasks) + 1)]
        for i, task in enumerate(tasks, start=1):
            for w in range(capacity + 1):
                best[i][w] = best[i - 1][w]
                if task.duration <= w:
                    with_task = best[i - 1][w - task.duration] + scores[i - 1]
                    if with_task > best[i][w]:
                        best[i][w] = with_task

        selected = []
        w = capacity
        for i in range(len(tasks), 0, -1):
            if best[i][w] != best[i - 1][w]:
                task = tasks[i - 1]
                selected.append(task)
                w -= task.duration
        selected.reverse()
        return selected

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority, shortest duration first within a tie."""
        return sorted(tasks, key=lambda task: (-PRIORITY_VALUES[task.priority], task.duration))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by time, earliest first, with untimed tasks last."""
        return sorted(tasks, key=lambda task: (task.time is None, task.time))
