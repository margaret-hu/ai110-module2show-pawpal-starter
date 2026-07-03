from dataclasses import dataclass, field
from datetime import date as Date


@dataclass
class Task:
    name: str
    duration: int
    priority: int
    type: str

    def updateTask(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def addTask(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    availability: str
    pets: list[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        pass

    def updateInfo(self) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    reasoning: str


@dataclass
class Plan:
    date: Date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)

    def display(self) -> str:
        pass

    def explain(self) -> str:
        pass


@dataclass
class Scheduler:
    available_minutes: int

    def build_plan(self, pet: Pet) -> Plan:
        pass

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass
