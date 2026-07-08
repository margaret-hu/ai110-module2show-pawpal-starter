import re
from dataclasses import dataclass, field
from datetime import date as Date, datetime, timedelta

_AVAILABILITY_RE = re.compile(
    r"(?:(?P<hours>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours))?"
    r"\s*(?:(?P<minutes>\d+)\s*(?:m|min|mins|minute|minutes))?",
    re.IGNORECASE,
)

PRIORITY_VALUES = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    type: str
    status: str = "incomplete"

    def mark_complete(self) -> None:
        """Mark this task's status as complete."""
        self.status = "complete"

    def updateTask(
        self,
        name: str | None = None,
        duration: int | None = None,
        priority: str | None = None,
        type: str | None = None,
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

    def __post_init__(self) -> None:
        self.remaining_minutes = self.available_minutes

    def build_plan(self, pet: Pet, date: Date) -> Plan:
        """Build a time-ordered plan for the given pet and date, prioritizing higher-priority tasks.

        Consumes from this scheduler's shared remaining_minutes pool, so calling this
        for multiple pets in a row correctly splits one owner's time budget between them
        instead of granting each pet the full available_minutes independently.
        """
        # order matters: sort by priority before filtering by time, so
        # higher-priority tasks aren't crowded out by earlier lower-priority ones
        ordered = self.sort_by_priority(pet.tasks)
        selected = self.filter_by_time(ordered)

        scheduled_tasks = []
        current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=8)
        for rank, task in enumerate(selected, start=1):
            reasoning = (
                f"Ranked #{rank} by priority ({task.priority}) and fits within the "
                f"{self.remaining_minutes} minute(s) remaining today."
            )
            scheduled_tasks.append(
                ScheduledTask(
                    task=task,
                    start_time=current_time.strftime("%H:%M"),
                    reasoning=reasoning,
                )
            )
            current_time += timedelta(minutes=task.duration)
            self.remaining_minutes -= task.duration

        return Plan(pet=pet, date=date, scheduled_tasks=scheduled_tasks)

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Select tasks, in order, that fit within the remaining minutes."""
        remaining = self.remaining_minutes
        selected = []
        for task in tasks:
            if task.duration <= remaining:
                selected.append(task)
                remaining -= task.duration
        return selected

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda task: PRIORITY_VALUES[task.priority], reverse=True)
