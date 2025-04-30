# Todo List System

This system provides a simple way to manage tasks in a text-based todo list that automatically moves completed tasks from the pending section to the completed section.

## How to Use

### File Structure

The system uses a single `todo.txt` file with the following structure:

```
# Pending Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

# Completed Tasks
- [x] Completed task 1
- [x] Completed task 2
```

### Adding Tasks

To add a new task, simply add a new line in the "Pending Tasks" section with the format:
```
- [ ] Your task description
```

### Marking Tasks as Complete

To mark a task as complete, change the checkbox from `[ ]` to `[x]`:
```
- [x] Your completed task
```

### Automatically Moving Completed Tasks

The system includes a Django management command that automatically moves completed tasks from the "Pending Tasks" section to the "Completed Tasks" section.

To run this command manually:
```
python manage.py update_todo
```

### Automated Updates

A batch file (`update_todo.bat`) is provided to run the update command. You can:

1. Run it manually by double-clicking the file
2. Schedule it to run automatically using Windows Task Scheduler

#### Setting up Windows Task Scheduler

1. Open Task Scheduler (search for it in the Start menu)
2. Click "Create Basic Task"
3. Enter a name (e.g., "Update Todo List") and description
4. Choose a trigger (e.g., Daily, Weekly)
5. Set the time and frequency
6. Choose "Start a program" as the action
7. Browse to select the `update_todo.bat` file
8. Complete the wizard

## Notes

- The system preserves the order of tasks within each section
- Completed tasks are moved to the end of the "Completed Tasks" section
- The file structure must be maintained with the exact section headers
- Tasks must use the exact format with `- [ ]` or `- [x]` for the checkboxes 