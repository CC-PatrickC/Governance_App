#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import re


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_intake.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Check if the command is for updating the todo list
    if len(sys.argv) > 1 and sys.argv[1] == 'update_todo':
        update_todo_list()
        return
    
    execute_from_command_line(sys.argv)


def update_todo_list():
    """Update the todo.txt file by moving completed tasks to the completed section."""
    try:
        # Read the todo.txt file
        with open('todo.txt', 'r') as file:
            content = file.read()
        
        # Split the content into sections
        sections = re.split(r'(## Completed Tasks\n|## Pending Tasks\n|### Scoring Page\n|### Final Scoring Page\n|## Future Enhancements\n)', content)
        
        # Find the completed tasks section and pending tasks section
        completed_section_index = -1
        pending_section_index = -1
        
        for i, section in enumerate(sections):
            if section == '## Completed Tasks\n':
                completed_section_index = i
            elif section == '## Pending Tasks\n':
                pending_section_index = i
        
        if completed_section_index == -1 or pending_section_index == -1:
            print("Could not find the required sections in the todo.txt file.")
            return
        
        # Get the completed tasks and pending tasks sections
        completed_tasks = sections[completed_section_index + 1]
        pending_tasks = sections[pending_section_index + 1]
        
        # Find completed tasks in the pending section
        completed_tasks_pattern = r'- \[x\] .*\n'
        completed_tasks_in_pending = re.findall(completed_tasks_pattern, pending_tasks)
        
        if not completed_tasks_in_pending:
            print("No completed tasks found in the pending section.")
            return
        
        # Remove completed tasks from the pending section
        pending_tasks_updated = re.sub(completed_tasks_pattern, '', pending_tasks)
        
        # Add completed tasks to the completed section
        completed_tasks_updated = completed_tasks + ''.join(completed_tasks_in_pending)
        
        # Update the sections
        sections[completed_section_index + 1] = completed_tasks_updated
        sections[pending_section_index + 1] = pending_tasks_updated
        
        # Join the sections back together
        updated_content = ''.join(sections)
        
        # Write the updated content back to the file
        with open('todo.txt', 'w') as file:
            file.write(updated_content)
        
        print(f"Successfully moved {len(completed_tasks_in_pending)} completed tasks to the completed section.")
    
    except Exception as e:
        print(f"Error updating todo list: {str(e)}")


if __name__ == '__main__':
    main()
