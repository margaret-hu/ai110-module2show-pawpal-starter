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
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
