from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner(name="Alex", availability="4h")

dog = Pet(name="Rex", species="Dog", breed="Labrador", age=3)
cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=2)

owner.addPet(dog)
owner.addPet(cat)

dog.addTask(Task(name="Morning walk", duration=30, priority="medium", type="exercise"))
dog.addTask(Task(name="Feed breakfast", duration=10, priority="high", type="feeding"))
cat.addTask(Task(name="Litter box cleaning", duration=15, priority="high", type="hygiene"))

scheduler = Scheduler(available_minutes=owner.available_minutes())
today = date.today()

print("Today's Schedule")
print("=================")
for pet in owner.pets:
    plan = scheduler.build_plan(pet, today)
    print(plan.display())
    print()
