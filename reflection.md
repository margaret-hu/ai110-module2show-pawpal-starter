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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

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
