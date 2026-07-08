from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
availability = st.text_input("Owner availability (e.g. 2h30m)", value="2h")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, availability=availability)

owner = st.session_state.owner
owner.updateInfo(name=owner_name, availability=availability)

st.divider()

st.subheader("Add a Pet")
col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="Mixed")
with col4:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    owner.addPet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_names = [p.name for p in owner.pets]
active_index = st.selectbox(
    "Active pet", range(len(owner.pets)), format_func=lambda i: pet_names[i]
)
pet = owner.pets[active_index]

st.markdown("### Tasks")
st.caption(f"Add a few tasks for {pet.name}. These feed into your scheduler below.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_type = st.selectbox("Type", ["exercise", "feeding", "grooming", "medication", "other"])
with col5:
    recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])

# Uncomment to test due_date rollover on recurring tasks (see Task.next_occurrence):
# due_date = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    pet.addTask(
        Task(
            name=task_title,
            duration=int(duration),
            priority=priority,
            type=task_type,
            recurrence=None if recurrence == "none" else recurrence,
            # due_date=due_date,
        )
    )

if pet.tasks:
    st.write("Current tasks:")
    for task in pet.tasks:
        task_col, status_col = st.columns([4, 1])
        with task_col:
            label = f"**{task.name}** — {task.duration} min, {task.priority} priority, {task.type}"
            if task.recurrence:
                label += f" (repeats {task.recurrence})"
            # if task.due_date:
            #     label += f" [due {task.due_date.isoformat()}]"
            st.write(label)
        with status_col:
            done = st.checkbox("Done", value=task.status == "complete", key=f"done-{id(task)}")
            if done and task.status != "complete":
                pet.complete_task(task)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(f"Generates a schedule for {pet.name} using your Scheduler class.")

if st.button("Generate schedule"):
    scheduler = Scheduler(available_minutes=owner.available_minutes())
    plan = scheduler.build_plan(pet, date.today())
    st.text(plan.display())
    st.text(plan.explain())
