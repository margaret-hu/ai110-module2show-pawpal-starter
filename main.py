from datetime import date

from pawpal_system import Owner, Pet, Scheduler, ScheduledTask, Task

owner = Owner(name="Alex", availability="4h")

dog = Pet(name="Rex", species="Dog", breed="Labrador", age=3)
cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=2)

owner.addPet(dog)
owner.addPet(cat)

# Added out of chronological order to exercise sort_by_time().
dog.addTask(Task(name="Evening walk", duration=20, priority="medium", type="exercise", time="18:00"))
dog.addTask(Task(name="Feed breakfast", duration=10, priority="high", type="feeding", time="07:00", recurrence="daily"))
dog.addTask(Task(name="Morning walk", duration=30, priority="medium", type="exercise", time="08:30"))
cat.addTask(Task(name="Litter box cleaning", duration=15, priority="high", type="hygiene", time="09:00"))

dog.complete_task(dog.tasks[1])  # Feed breakfast — daily, so a fresh instance is queued up automatically

scheduler = Scheduler(available_minutes=owner.available_minutes())
today = date.today()

print("Today's Schedule")
print("=================")
for pet in owner.pets:
    plan = scheduler.build_plan(pet, today)
    print(plan.display())
    print()

print("Conflict Check")
print("==============")
# build_plan actively avoids collisions on its own, so to exercise the conflict detector
# we simulate two tasks manually pinned to the same time afterward — e.g. a user dragging
# both to 09:00 in the UI, which bypasses the optimizer's own conflict avoidance.
vet_checkup = Task(name="Vet checkup", duration=20, priority="high", type="health", time="09:00")
grooming = Task(name="Grooming", duration=20, priority="high", type="hygiene", time="09:00")
scheduler.scheduled.append(
    (today, dog, ScheduledTask(task=vet_checkup, start_time="09:00", reasoning="Manually pinned to 09:00."))
)
scheduler.scheduled.append(
    (today, cat, ScheduledTask(task=grooming, start_time="09:00", reasoning="Manually pinned to 09:00."))
)
warning = scheduler.conflict_warning()
print(warning if warning else "No conflicts detected.")
print()

print("Rex's Tasks Sorted by Time")
print("==========================")
for task in scheduler.sort_by_time(dog.tasks):
    print(f"  {task.time} — {task.name}")
print()

print("Completed Tasks (all pets)")
print("===========================")
for task in owner.filter_tasks(status="complete"):
    print(f"  {task.name}")
print()

print("Rex's Tasks Only")
print("================")
for task in owner.filter_tasks(pet_name="Rex"):
    print(f"  {task.name} [{task.status}, recurrence={task.recurrence}]")
