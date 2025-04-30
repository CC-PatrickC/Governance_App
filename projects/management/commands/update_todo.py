import os
import re
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Updates todo.txt by moving completed tasks from pending to completed section'

    def handle(self, *args, **options):
        todo_file = 'todo.txt'
        
        # Check if todo.txt exists
        if not os.path.exists(todo_file):
            self.stdout.write(self.style.ERROR(f'File {todo_file} not found'))
            return
            
        try:
            # Read the current content
            with open(todo_file, 'r') as f:
                content = f.read()
                
            # Split content into sections
            sections = re.split(r'(# Pending Tasks|# Completed Tasks)', content)
            
            if len(sections) < 5:  # We expect at least 5 parts: before pending, pending header, pending content, completed header, completed content
                self.stdout.write(self.style.ERROR('Invalid todo.txt format'))
                return
                
            # Extract tasks from pending section
            pending_tasks = sections[3].strip().split('\n')
            completed_tasks = sections[5].strip().split('\n') if len(sections) > 5 else []
            
            # Find completed tasks in pending section
            new_completed = []
            remaining_pending = []
            
            for task in pending_tasks:
                if task.strip().startswith('- [x]'):
                    new_completed.append(task)
                elif task.strip():  # Only add non-empty lines
                    remaining_pending.append(task)
                    
            # Update sections
            new_pending = '\n'.join(remaining_pending)
            new_completed = '\n'.join(completed_tasks + new_completed) if completed_tasks else '\n'.join(new_completed)
            
            # Write updated content
            with open(todo_file, 'w') as f:
                f.write('# Pending Tasks\n')
                f.write(new_pending)
                f.write('\n\n# Completed Tasks\n')
                f.write(new_completed)
                
            self.stdout.write(self.style.SUCCESS(f'Successfully moved {len(new_completed)} completed tasks'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating todo list: {str(e)}')) 