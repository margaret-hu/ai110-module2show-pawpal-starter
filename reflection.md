# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.\
  The system is designed around three core user actions:
    1. **Set up owner and pet profiles** — A user enters their name and basic information about their pet (name, species, and any relevant preferences). This context shapes how the scheduler prioritizes and explains tasks.
    2. **Define care tasks** — A user adds tasks representing things their pet needs each day (such as walks, feeding, or medication), specifying how long each task takes and how important it is relative to others.
    3. **Generate and review a daily plan** — A user triggers the scheduler, which selects and orders tasks based on priority and available time, then presents a time-ordered plan with a brief explanation of why each task was included.
- What classes did you include, and what responsibilities did you assign to each?\
  The design includes six classes, split between domain data, scheduling logic, and output: 
    - **Owner** holds identity/context info (name, availability) and manages the pets it owns (addPet, updateInfo). 
    - **Pet** holds profile data (name, species, breed, age) and manages the tasks assigned to it (addTask). 
    - **Task** represents a single care need (name, duration, priority, type) and can be edited (updateTask). 
    - **Scheduler** is the core logic class — it takes a Pet's tasks and available time, filters them by time (filter_by_time), orders them by priority (sort_by_priority), and assembles a Plan (build_plan). 
    - **Plan** is the scheduler's output for a given date; it holds an ordered list of ScheduledTasks and can render itself (display) or justify its choices (explain). 
    - **ScheduledTask** wraps a Task with a concrete start_time and reasoning, connecting the abstract task to its place in the concrete daily plan. 
  
  Responsibilities are split so that Owner/Pet/Task are plain data holders describing "what needs to happen," while Scheduler owns all the decision logic ("what happens when"), and Plan/ScheduledTask are read-only output objects that present the result — keeping scheduling logic out of the domain classes and out of the presentation classes.

**b. Design changes**

- Did your design change during implementation? Yes.
- If yes, describe at least one change and why you made it.\
  While reviewing the skeleton I found three gaps between the classes as originally modeled:
    1. `Scheduler.build_plan(pet)` had no `date` parameter, even though the `Plan` it returns requires one — there was no way to know which day a plan was being built for. I added a `date` argument to `build_plan`.
    2. `Plan` had no reference back to the `Pet` it was built for, so a `Plan` object on its own couldn't say whose plan it was. I added a `pet` field to `Plan`.
    3. `Owner.availability` (a string) and `Scheduler.available_minutes` (an int) represented the same real-world constraint but had no defined relationship, leaving it unclear how one becomes the other. I added an `Owner.available_minutes()` method as the conversion point between the two.
  
  I made these changes because they were structural gaps that would have caused ambiguity or bugs once the methods were implemented, not because the original responsibilities split (data holders vs. scheduling logic vs. output) was wrong.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)? Time and priority
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.\
  `Scheduler.filter_by_time()` uses 0/1 knapsack dynamic programming instead of a greedy priority pass to decide which tasks fit in the available time. A greedy approach (take tasks in priority order until time runs out) is faster but can waste the budget — e.g. one long "high" priority task can crowd out several "medium" tasks that together would fit and deliver more total value. Knapsack is more expensive (O(n × capacity) in time and space, versus O(n log n) for greedy), but it guarantees the selected subset maximizes total priority value for the given time budget.
- Why is that tradeoff reasonable for this scenario?\
  Each pet's task list is small (a handful of daily care tasks) and the time budget is bounded to a day's worth of minutes, so the O(n × capacity) DP table is cheap in practice — there's no real performance cost to paying for optimality here. That makes it a good trade: better use of the owner's limited time with no meaningful runtime penalty. (Priority sorting is still used afterward, in `sort_by_priority()`, but only to *order* the already-selected tasks throughout the day, not to decide which ones make the cut.)

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?\
  I used AI throughout, not just at the UML stage. Early on I used it to brainstorm which classes and methods belonged in the design. Later I used it for implementation-level work: wiring the Streamlit UI in `app.py` to real `Owner`/`Pet`/`Task`/`Scheduler` objects instead of placeholder inputs, debugging a bug where `Scheduler.available_minutes` was being treated as a fresh budget for every pet instead of one shared pool across pets in the same `build_plan` loop, and adding the `Task.status`/`mark_complete()` feature along with matching docstrings and pytest tests.
- What kinds of prompts or questions were most helpful?\
  Prompts that named a concrete, observable gap were the most productive — for example, describing the specific symptom of the shared-time-budget bug (each pet getting the full budget instead of splitting one owner's time) rather than just saying "check the scheduler for bugs." Similarly, "replace the placeholder inputs in app.py with the real domain classes" gave a clearer target than a vague "improve the UI" request. Open-ended prompts were more useful early, for brainstorming design options; specific, symptom-first prompts were more useful once I was debugging or extending working code.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.\
The UML design model the AI suggested was missing methods for adding and updating a task on the domain objects.
- How did you evaluate or verify what the AI suggested?\
I checked the design against the assignment requirements, which state that the final app should let a user add and edit tasks. Since the AI's suggested methods didn't cover that, I added the missing methods myself.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?\
  The test suite (`tests/test_pawpal.py`) covers four areas:
    1. **Task lifecycle** — marking a task complete, `updateTask` only changing the fields passed in, and recurrence chaining (`next_occurrence` for daily/weekly tasks, unrecognized recurrence returning `None`, and multiple completions in a row producing the right sequence of due dates).
    2. **Owner/Pet aggregation** — `addPet`/`addTask` updating counts correctly, `all_tasks`/`filter_tasks` aggregating and filtering across multiple pets, and `Owner.available_minutes()` parsing the various availability string formats ("2:30", "1h 30m", "45 min", "90", "1.5h", empty string, and non-numeric garbage).
    3. **Scheduler selection and ordering** — `filter_by_time`'s knapsack logic, including edge cases: zero capacity, a task longer than the whole budget, and equal-priority-value ties broken by using less time; `sort_by_priority` ordering high-to-low-then-shorter-first and raising on an unrecognized priority; `sort_by_time` ordering by clock time and pushing untimed tasks last (plus a test documenting the current non-zero-padded-hour string-sort bug, e.g. "10:00" sorting before "9:00").
    4. **`build_plan` integration** — tasks scheduled back-to-back from 8am, the shared time budget being split (not duplicated) across multiple pets in the same scheduling run, conflict detection/avoidance across pets on the same date (and correctly ignoring same-time tasks on different dates), completed tasks being excluded from the plan, and calling `build_plan` twice for the same pet/date not double-scheduling.
- Why were these tests important?\
  These tests target the parts of the system most likely to have subtle bugs: date/recurrence arithmetic (off-by-one errors are easy to introduce), the knapsack tradeoff called out in section 2b (its correctness is only meaningful if the selection is actually optimal, not just "reasonable-looking"), and the shared-time-budget behavior that was previously broken (see section 3a) — that test exists specifically to prevent the fixed bug from regressing. The edge-case tests (zero capacity, ties, non-zero-padded time strings) also matter because these are exactly the inputs a developer is likely to overlook when refactoring, so locking in expected behavior now makes future changes safer.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
