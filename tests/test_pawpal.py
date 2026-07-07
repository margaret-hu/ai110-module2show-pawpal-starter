from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=20, priority="high", type="exercise")
    assert task.status == "incomplete"

    task.mark_complete()

    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", breed="shiba", age=3)
    assert len(pet.tasks) == 0

    task = Task(name="Feed", duration=10, priority="medium", type="feeding")
    pet.addTask(task)

    assert len(pet.tasks) == 1
