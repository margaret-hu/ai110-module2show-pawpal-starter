from datetime import date, datetime

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=20, priority="high", type="exercise")
    assert task.status == "incomplete"

    task.mark_complete()

    assert task.status == "complete"


def test_mark_complete_without_recurrence_returns_none():
    task = Task(name="One-off vet visit", duration=30, priority="high", type="health")

    next_task = task.mark_complete()

    assert next_task is None


def test_mark_complete_with_recurrence_returns_next_occurrence():
    task = Task(
        name="Morning walk",
        duration=20,
        priority="high",
        type="exercise",
        recurrence="daily",
        due_date=date(2026, 7, 7),
    )

    next_task = task.mark_complete()

    assert task.status == "complete"
    assert next_task is not None
    assert next_task.status == "incomplete"
    assert next_task.due_date == date(2026, 7, 8)
    assert next_task.name == "Morning walk"


def test_update_task_only_changes_given_fields():
    task = Task(name="Feed", duration=10, priority="medium", type="feeding")

    task.updateTask(duration=15, priority="high")

    assert task.name == "Feed"
    assert task.duration == 15
    assert task.priority == "high"
    assert task.type == "feeding"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    assert len(pet.tasks) == 0

    task = Task(name="Feed", duration=10, priority="medium", type="feeding")
    pet.addTask(task)

    assert len(pet.tasks) == 1


def test_complete_task_adds_next_occurrence_to_pet():
    pet = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    task = Task(
        name="Feed",
        duration=10,
        priority="medium",
        type="feeding",
        recurrence="daily",
        due_date=date(2026, 7, 7),
    )
    pet.addTask(task)

    pet.complete_task(task)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date(2026, 7, 8)
    assert pet.tasks[1].status == "incomplete"


def test_owner_add_pet_and_update_info():
    owner = Owner(name="Alex", availability="2h")
    pet = Pet(name="Mochi", species="dog", breed="shiba", age=3)

    owner.addPet(pet)
    owner.updateInfo(name="Alexis")

    assert owner.pets == [pet]
    assert owner.name == "Alexis"
    assert owner.availability == "2h"


def test_owner_all_tasks_aggregates_across_pets():
    owner = Owner(name="Alex", availability="2h")
    pet1 = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    pet2 = Pet(name="Rex", species="dog", breed="lab", age=5)
    pet1.addTask(Task(name="Feed", duration=10, priority="medium", type="feeding"))
    pet2.addTask(Task(name="Walk", duration=20, priority="high", type="exercise"))
    owner.addPet(pet1)
    owner.addPet(pet2)

    tasks = owner.all_tasks()

    assert {task.name for task in tasks} == {"Feed", "Walk"}


def test_owner_filter_tasks_by_status_and_pet_name():
    owner = Owner(name="Alex", availability="2h")
    pet1 = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    pet2 = Pet(name="Rex", species="dog", breed="lab", age=5)
    feed = Task(name="Feed", duration=10, priority="medium", type="feeding")
    walk = Task(name="Walk", duration=20, priority="high", type="exercise")
    feed.mark_complete()
    pet1.addTask(feed)
    pet2.addTask(walk)
    owner.addPet(pet1)
    owner.addPet(pet2)

    assert owner.filter_tasks(pet_name="Rex") == [walk]
    assert owner.filter_tasks(status="complete") == [feed]
    assert owner.filter_tasks(status="incomplete", pet_name="Mochi") == []


def test_owner_available_minutes_parses_various_formats():
    assert Owner(name="Alex", availability="2:30").available_minutes() == 150
    assert Owner(name="Alex", availability="1h 30m").available_minutes() == 90
    assert Owner(name="Alex", availability="45 min").available_minutes() == 45
    assert Owner(name="Alex", availability="90").available_minutes() == 90
    assert Owner(name="Alex", availability="").available_minutes() == 0


def test_filter_by_time_prefers_more_total_value_over_one_long_task():
    tasks = [
        Task(name="Long high", duration=60, priority="high", type="exercise"),
        Task(name="Short medium A", duration=20, priority="medium", type="feeding"),
        Task(name="Short medium B", duration=20, priority="medium", type="feeding"),
        Task(name="Short medium C", duration=20, priority="medium", type="feeding"),
    ]
    scheduler = Scheduler(available_minutes=60)

    selected = scheduler.filter_by_time(tasks)

    assert {task.name for task in selected} == {
        "Short medium A",
        "Short medium B",
        "Short medium C",
    }


def test_sort_by_priority_orders_high_to_low_then_shorter_first():
    tasks = [
        Task(name="Low", duration=10, priority="low", type="play"),
        Task(name="High long", duration=30, priority="high", type="exercise"),
        Task(name="High short", duration=10, priority="high", type="exercise"),
    ]
    scheduler = Scheduler(available_minutes=100)

    ordered = scheduler.sort_by_priority(tasks)

    assert [task.name for task in ordered] == ["High short", "High long", "Low"]


def test_sort_by_time_returns_tasks_in_chronological_order():
    tasks = [
        Task(name="Noon", duration=10, priority="low", type="play", time="12:00"),
        Task(name="Morning", duration=10, priority="low", type="play", time="07:00"),
        Task(name="Evening", duration=10, priority="low", type="play", time="18:00"),
    ]
    scheduler = Scheduler(available_minutes=100)

    ordered = scheduler.sort_by_time(tasks)

    assert [task.name for task in ordered] == ["Morning", "Noon", "Evening"]


def test_sort_by_time_puts_untimed_tasks_last():
    tasks = [
        Task(name="No time", duration=10, priority="low", type="play"),
        Task(name="Later", duration=10, priority="low", type="play", time="14:00"),
        Task(name="Earlier", duration=10, priority="low", type="play", time="08:00"),
    ]
    scheduler = Scheduler(available_minutes=100)

    ordered = scheduler.sort_by_time(tasks)

    assert [task.name for task in ordered] == ["Earlier", "Later", "No time"]


def test_build_plan_schedules_tasks_back_to_back_starting_at_8am():
    pet = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet.addTask(Task(name="Walk", duration=30, priority="high", type="exercise"))
    pet.addTask(Task(name="Feed", duration=10, priority="medium", type="feeding"))
    scheduler = Scheduler(available_minutes=120)

    plan = scheduler.build_plan(pet, date(2026, 7, 7))

    start_times = [scheduled.start_time for scheduled in plan.scheduled_tasks]
    assert start_times == ["08:00", "08:30"]
    assert scheduler.remaining_minutes == 120 - 30 - 10


def test_build_plan_splits_shared_time_budget_across_pets():
    pet1 = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet1.addTask(Task(name="Walk", duration=40, priority="high", type="exercise"))
    pet2 = Pet(name="Milo", species="cat", breed="tabby", age=2)
    pet2.addTask(Task(name="Groom", duration=40, priority="high", type="grooming"))
    scheduler = Scheduler(available_minutes=60)
    d = date(2026, 7, 7)

    plan1 = scheduler.build_plan(pet1, d)
    plan2 = scheduler.build_plan(pet2, d)

    assert len(plan1.scheduled_tasks) == 1
    assert len(plan2.scheduled_tasks) == 0
    assert scheduler.remaining_minutes == 20


def test_build_plan_avoids_conflicts_across_pets_on_same_date():
    pet1 = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet1.addTask(Task(name="Walk", duration=30, priority="high", type="exercise"))
    pet2 = Pet(name="Milo", species="cat", breed="tabby", age=2)
    pet2.addTask(Task(name="Groom", duration=15, priority="high", type="grooming"))
    scheduler = Scheduler(available_minutes=200)
    d = date(2026, 7, 7)

    scheduler.build_plan(pet1, d)
    plan2 = scheduler.build_plan(pet2, d)

    assert plan2.scheduled_tasks[0].start_time == "08:30"
    assert scheduler.find_conflicts() == []
    assert scheduler.conflict_warning() is None


def test_next_free_start_skips_multiple_busy_intervals():
    busy = [
        (datetime(2026, 7, 7, 8, 0), datetime(2026, 7, 7, 8, 30)),
        (datetime(2026, 7, 7, 8, 30), datetime(2026, 7, 7, 9, 0)),
    ]

    start = Scheduler._next_free_start(datetime(2026, 7, 7, 8, 0), 20, busy)

    assert start == datetime(2026, 7, 7, 9, 0)


def test_find_conflicts_ignores_same_time_overlap_on_different_dates():
    pet1 = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet1.addTask(Task(name="Walk", duration=30, priority="high", type="exercise"))
    pet2 = Pet(name="Milo", species="cat", breed="tabby", age=2)
    pet2.addTask(Task(name="Groom", duration=15, priority="high", type="grooming"))
    scheduler = Scheduler(available_minutes=200)

    scheduler.build_plan(pet1, date(2026, 7, 7))
    scheduler.build_plan(pet2, date(2026, 7, 8))

    assert scheduler.find_conflicts() == []
    assert scheduler.conflict_warning() is None


def test_find_conflicts_detects_manual_overlap_on_same_date():
    pet1 = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet1.addTask(Task(name="Walk", duration=30, priority="high", type="exercise"))
    pet2 = Pet(name="Milo", species="cat", breed="tabby", age=2)
    pet2.addTask(Task(name="Groom", duration=15, priority="high", type="grooming"))
    scheduler = Scheduler(available_minutes=200)
    d = date(2026, 7, 7)

    plan1 = scheduler.build_plan(pet1, d)
    plan2 = scheduler.build_plan(pet2, d)
    assert scheduler.find_conflicts() == []

    plan2.scheduled_tasks[0].start_time = plan1.scheduled_tasks[0].start_time

    conflicts = scheduler.find_conflicts()
    assert len(conflicts) == 1
    assert scheduler.conflict_warning() is not None


def test_filter_by_time_with_zero_capacity_selects_nothing():
    tasks = [Task(name="Feed", duration=10, priority="high", type="feeding")]
    scheduler = Scheduler(available_minutes=0)

    assert scheduler.filter_by_time(tasks) == []


def test_filter_by_time_excludes_task_longer_than_capacity():
    fits = Task(name="Fits", duration=10, priority="low", type="play")
    tasks = [
        Task(name="Too long", duration=50, priority="high", type="exercise"),
        fits,
    ]
    scheduler = Scheduler(available_minutes=20)

    assert scheduler.filter_by_time(tasks) == [fits]


def test_filter_by_time_breaks_equal_priority_value_ties_by_choosing_less_time():
    # {"One long"} and {"Short A", "Short B"} both total priority value 2 (medium),
    # but the pair uses only 12 of the 15 available minutes vs. 15 for the single task.
    tasks = [
        Task(name="One long", duration=15, priority="medium", type="exercise"),
        Task(name="Short A", duration=6, priority="low", type="play"),
        Task(name="Short B", duration=6, priority="low", type="play"),
    ]
    scheduler = Scheduler(available_minutes=15)

    selected = scheduler.filter_by_time(tasks)

    assert {task.name for task in selected} == {"Short A", "Short B"}


def test_build_plan_stops_selecting_once_shared_budget_exhausted_mid_pet():
    pet1 = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet1.addTask(Task(name="Walk", duration=50, priority="high", type="exercise"))
    pet2 = Pet(name="Milo", species="cat", breed="tabby", age=2)
    pet2.addTask(Task(name="Groom", duration=15, priority="high", type="grooming"))
    pet2.addTask(Task(name="Feed", duration=5, priority="medium", type="feeding"))
    scheduler = Scheduler(available_minutes=60)
    d = date(2026, 7, 7)

    scheduler.build_plan(pet1, d)
    plan2 = scheduler.build_plan(pet2, d)

    assert [scheduled.task.name for scheduled in plan2.scheduled_tasks] == ["Feed"]
    assert scheduler.remaining_minutes == 5


def test_next_free_start_chains_through_overlapping_busy_intervals():
    busy = [
        (datetime(2026, 7, 7, 8, 0), datetime(2026, 7, 7, 8, 20)),
        (datetime(2026, 7, 7, 8, 25), datetime(2026, 7, 7, 8, 45)),
    ]

    # Naive start (8:10) lands inside the first interval; the 20-minute window
    # that follows also spills into the second interval, so it must chain past both.
    start = Scheduler._next_free_start(datetime(2026, 7, 7, 8, 10), 20, busy)

    assert start == datetime(2026, 7, 7, 8, 45)


def test_next_occurrence_preserves_none_due_date():
    task = Task(
        name="Brush",
        duration=5,
        priority="low",
        type="grooming",
        recurrence="weekly",
        due_date=None,
    )

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date is None
    assert next_task.status == "incomplete"


def test_owner_available_minutes_handles_decimal_hours():
    assert Owner(name="Alex", availability="1.5h").available_minutes() == 90


def test_owner_available_minutes_returns_zero_for_non_numeric_garbage():
    assert Owner(name="Alex", availability="none").available_minutes() == 0


def test_build_plan_excludes_completed_tasks():
    pet = Pet(name="Rex", species="dog", breed="lab", age=3)
    task = Task(name="Walk", duration=20, priority="high", type="exercise")
    pet.addTask(task)
    pet.complete_task(task)
    assert task.status == "complete"

    scheduler = Scheduler(available_minutes=60)
    plan = scheduler.build_plan(pet, date(2026, 7, 7))

    assert plan.scheduled_tasks == []
    assert scheduler.remaining_minutes == 60


def test_recurrence_chains_correctly_across_multiple_completions():
    pet = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    task = Task(
        name="Walk",
        duration=15,
        priority="high",
        type="exercise",
        recurrence="daily",
        due_date=date(2026, 7, 7),
    )
    pet.addTask(task)

    pet.complete_task(task)
    pet.complete_task(pet.tasks[1])

    assert [t.due_date for t in pet.tasks] == [
        date(2026, 7, 7),
        date(2026, 7, 8),
        date(2026, 7, 9),
    ]
    assert [t.status for t in pet.tasks] == ["complete", "complete", "incomplete"]


def test_next_occurrence_weekly_adds_seven_days():
    task = Task(
        name="Grooming",
        duration=30,
        priority="medium",
        type="grooming",
        recurrence="weekly",
        due_date=date(2026, 7, 7),
    )

    next_task = task.next_occurrence()

    assert next_task.due_date == date(2026, 7, 14)


def test_next_occurrence_returns_none_for_unrecognized_recurrence():
    task = Task(
        name="Vet checkup",
        duration=30,
        priority="high",
        type="health",
        recurrence="monthly",
        due_date=date(2026, 7, 7),
    )

    assert task.next_occurrence() is None


def test_sort_by_priority_raises_for_unrecognized_priority():
    tasks = [Task(name="Mystery", duration=10, priority="urgent", type="play")]
    scheduler = Scheduler(available_minutes=100)

    with pytest.raises(KeyError):
        scheduler.sort_by_priority(tasks)


def test_sort_by_time_misorders_non_zero_padded_hours():
    tasks = [
        Task(name="Ten AM", duration=10, priority="low", type="play", time="10:00"),
        Task(name="Nine AM", duration=10, priority="low", type="play", time="9:00"),
    ]
    scheduler = Scheduler(available_minutes=100)

    ordered = scheduler.sort_by_time(tasks)

    # Documents current behavior: this is a plain string sort, so the
    # non-zero-padded "9:00" sorts after "10:00" even though 9 AM is earlier.
    assert [task.name for task in ordered] == ["Ten AM", "Nine AM"]


def test_build_plan_called_twice_for_same_pet_and_date_does_not_double_schedule():
    pet = Pet(name="Rex", species="dog", breed="lab", age=3)
    pet.addTask(Task(name="Walk", duration=20, priority="high", type="exercise"))
    scheduler = Scheduler(available_minutes=100)
    d = date(2026, 7, 7)

    plan1 = scheduler.build_plan(pet, d)
    plan2 = scheduler.build_plan(pet, d)

    assert [s.task.name for s in plan1.scheduled_tasks] == ["Walk"]
    assert plan2.scheduled_tasks == []
    assert scheduler.remaining_minutes == 100 - 20
