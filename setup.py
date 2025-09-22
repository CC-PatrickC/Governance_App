#!/usr/bin/env python3
"""
Setup script for Patrick's Governance App for CC ITS
This script helps automate the initial setup process.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def generate_secret_key():
    """Generate a new Django secret key."""
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))

def create_env_file():
    """Create a .env file with default values."""
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    secret_key = generate_secret_key()
    env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/

# Django Allauth Settings
SITE_ID=1
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_USERNAME_REQUIRED=False
ACCOUNT_AUTHENTICATION_METHOD=email
ACCOUNT_EMAIL_VERIFICATION=mandatory

# Time Zone
TIME_ZONE=UTC
USE_TZ=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file with default settings")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Patrick's Governance App for CC ITS")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("✗ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Create virtual environment
    if not Path('venv').exists():
        print("\n📦 Creating virtual environment...")
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    else:
        print("✓ Virtual environment already exists")
    
    # Step 2: Activate virtual environment and install dependencies
    print("\n📚 Installing dependencies...")
    
    # Determine the correct activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
    
    if not run_command(f'{pip_cmd} install -r requirements.txt', 'Installing Python dependencies'):
        sys.exit(1)
    
    # Step 3: Create .env file
    print("\n⚙️  Setting up environment variables...")
    if not create_env_file():
        sys.exit(1)
    
    # Step 4: Run migrations
    print("\n🗄️  Setting up database...")
    if not run_command(f'{pip_cmd} install django', 'Installing Django'):
        sys.exit(1)
    
    if not run_command(f'{pip_cmd} run python manage.py migrate', 'Running database migrations'):
        sys.exit(1)
    
    # Step 5: Create superuser (optional)
    print("\n👤 Superuser creation...")
    print("You can create a superuser account now, or run 'python manage.py createsuperuser' later.")
    create_superuser = input("Create superuser now? (y/n): ").lower().strip()
    
    if create_superuser == 'y':
        print("Please follow the prompts to create your superuser account:")
        run_command(f'{pip_cmd} run python manage.py createsuperuser', 'Creating superuser')
    
    # Step 6: Collect static files
    print("\n📁 Collecting static files...")
    run_command(f'{pip_cmd} run python manage.py collectstatic --noinput', 'Collecting static files')
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the development server:")
    print("   python manage.py runserver")
    print("3. Open your browser and go to: http://127.0.0.1:8000/")
    print("\nFor more information, see the README.md file.")

if __name__ == '__main__':
    main()










