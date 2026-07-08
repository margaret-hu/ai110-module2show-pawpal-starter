# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Today's Schedule
=================
Daily plan for Rex (Labrador) — 2026-07-07:
  08:00 — Feed breakfast (10 min) [priority: high]
  08:10 — Feed breakfast (10 min) [priority: high]
  08:20 — Evening walk (20 min) [priority: medium]
  08:40 — Morning walk (30 min) [priority: medium]

Daily plan for Whiskers (Siamese) — 2026-07-07:
  09:10 — Litter box cleaning (15 min) [priority: high]
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 35 tests in `tests/test_pawpal.py` cover:

- **Task lifecycle** — marking tasks complete, `updateTask` partial updates, and recurrence chaining (daily/weekly `next_occurrence`, unrecognized recurrence, multi-completion sequences)
- **Owner/Pet aggregation** — adding pets/tasks, aggregating and filtering tasks across pets, and parsing the many `availability` string formats into minutes
- **Scheduler selection and ordering** — the `filter_by_time` knapsack logic (including zero capacity, over-budget tasks, and priority-value ties), `sort_by_priority`, and `sort_by_time` (including untimed tasks and a documented non-zero-padded-hour edge case)
- **`build_plan` integration** — back-to-back scheduling from 8am, splitting one shared time budget across multiple pets, conflict detection/avoidance across pets and dates, excluding completed tasks, and idempotency when called twice for the same pet/date

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\marga\ai110-module2show-pawpal-starter\ai110-module2show-pawpal-starter
collecting ... collected 35 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  2%]
tests/test_pawpal.py::test_mark_complete_without_recurrence_returns_none PASSED [  5%]
tests/test_pawpal.py::test_mark_complete_with_recurrence_returns_next_occurrence PASSED [  8%]
tests/test_pawpal.py::test_update_task_only_changes_given_fields PASSED  [ 11%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 14%]
tests/test_pawpal.py::test_complete_task_adds_next_occurrence_to_pet PASSED [ 17%]
tests/test_pawpal.py::test_owner_add_pet_and_update_info PASSED          [ 20%]
tests/test_pawpal.py::test_owner_all_tasks_aggregates_across_pets PASSED [ 22%]
tests/test_pawpal.py::test_owner_filter_tasks_by_status_and_pet_name PASSED [ 25%]
tests/test_pawpal.py::test_owner_available_minutes_parses_various_formats PASSED [ 28%]
tests/test_pawpal.py::test_filter_by_time_prefers_more_total_value_over_one_long_task PASSED [ 31%]
tests/test_pawpal.py::test_sort_by_priority_orders_high_to_low_then_shorter_first PASSED [ 34%]
tests/test_pawpal.py::test_sort_by_time_returns_tasks_in_chronological_order PASSED [ 37%]
tests/test_pawpal.py::test_sort_by_time_puts_untimed_tasks_last PASSED   [ 40%]
tests/test_pawpal.py::test_build_plan_schedules_tasks_back_to_back_starting_at_8am PASSED [ 42%]
tests/test_pawpal.py::test_build_plan_splits_shared_time_budget_across_pets PASSED [ 45%]
tests/test_pawpal.py::test_build_plan_avoids_conflicts_across_pets_on_same_date PASSED [ 48%]
tests/test_pawpal.py::test_next_free_start_skips_multiple_busy_intervals PASSED [ 51%]
tests/test_pawpal.py::test_find_conflicts_ignores_same_time_overlap_on_different_dates PASSED [ 54%]
tests/test_pawpal.py::test_find_conflicts_detects_manual_overlap_on_same_date PASSED [ 57%]
tests/test_pawpal.py::test_filter_by_time_with_zero_capacity_selects_nothing PASSED [ 60%]
tests/test_pawpal.py::test_filter_by_time_excludes_task_longer_than_capacity PASSED [ 62%]
tests/test_pawpal.py::test_filter_by_time_breaks_equal_priority_value_ties_by_choosing_less_time PASSED [ 65%]
tests/test_pawpal.py::test_build_plan_stops_selecting_once_shared_budget_exhausted_mid_pet PASSED [ 68%]
tests/test_pawpal.py::test_next_free_start_chains_through_overlapping_busy_intervals PASSED [ 71%]
tests/test_pawpal.py::test_next_occurrence_preserves_none_due_date PASSED [ 74%]
tests/test_pawpal.py::test_owner_available_minutes_handles_decimal_hours PASSED [ 77%]
tests/test_pawpal.py::test_owner_available_minutes_returns_zero_for_non_numeric_garbage PASSED [ 80%]
tests/test_pawpal.py::test_build_plan_excludes_completed_tasks PASSED    [ 82%]
tests/test_pawpal.py::test_recurrence_chains_correctly_across_multiple_completions PASSED [ 85%]
tests/test_pawpal.py::test_next_occurrence_weekly_adds_seven_days PASSED [ 88%]
tests/test_pawpal.py::test_next_occurrence_returns_none_for_unrecognized_recurrence PASSED [ 91%]
tests/test_pawpal.py::test_sort_by_priority_raises_for_unrecognized_priority PASSED [ 94%]
tests/test_pawpal.py::test_sort_by_time_misorders_non_zero_padded_hours PASSED [ 97%]
tests/test_pawpal.py::test_build_plan_called_twice_for_same_pet_and_date_does_not_double_schedule PASSED [100%]

============================= 35 passed in 0.03s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

The core scheduling logic (knapsack selection, priority/time ordering, shared-budget handling, conflict detection, and recurrence) is well covered and all 35 tests pass, including several edge cases (zero capacity, over-budget tasks, priority ties). One star is held back because `sort_by_time` has a known bug with non-zero-padded hour strings (documented, not fixed, in `test_sort_by_time_misorders_non_zero_padded_hours`), and the Streamlit UI layer in `app.py` isn't covered by automated tests.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | `sort_by_priority` orders tasks highest-to-lowest priority, breaking ties by shorter duration first. `sort_by_time` orders tasks by their `time` field, earliest first, with untimed tasks pushed to the end. |
| Filtering | `Scheduler.filter_by_time()`, `Owner.filter_tasks()` | `filter_by_time` selects the subset of a pet's tasks that maximizes total priority within the owner's remaining minutes, using a 0/1 knapsack (duration = weight, priority = value) instead of a greedy cutoff, so several lower-priority tasks aren't crowded out by one long high-priority task. `filter_tasks` filters an owner's tasks by completion `status` and/or `pet_name`, independent of scheduling. |
| Conflict detection | `Scheduler.find_conflicts()`, `Scheduler.conflict_warning()` | `find_conflicts` compares every pair of tasks scheduled on the same date (across all pets) and reports any whose time windows overlap. `Scheduler.build_plan()` also consults each date's already-busy intervals (via `Scheduler._next_free_start()`) to push a new task's start time past conflicts before they happen, so `find_conflicts`/`conflict_warning` mainly guard against conflicts introduced by manually editing a task's time afterward. |
| Recurring tasks | `Task.next_occurrence()`, `Task.mark_complete()`, `Pet.complete_task()` | `next_occurrence` builds a fresh incomplete `Task` advanced by one day (`daily`) or one week (`weekly`) based on the task's `recurrence` field, or returns `None` if it doesn't recur. `mark_complete` marks a task complete and returns its next occurrence (if any); `Pet.complete_task` calls this and automatically appends the new occurrence to the pet's task list. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
