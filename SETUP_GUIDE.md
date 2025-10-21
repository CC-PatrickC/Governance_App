# Setup Guide for Patrick's Governance App

This guide explains how to set up the Django application when you download it from GitHub.

## What Happens When Someone Downloads Your Project

When someone clones your repository from GitHub, they get:
- ✅ All your Django code
- ✅ Templates and static files
- ✅ Database migrations
- ✅ Requirements file
- ❌ **NOT** your database (db.sqlite3)
- ❌ **NOT** your environment variables (.env)
- ❌ **NOT** your virtual environment (venv/)
- ❌ **NOT** your uploaded files (media/)

## Quick Start (3 Steps)

### Option 1: Automated Setup (Recommended)

**Windows Users:**
```bash
git clone <your-repo-url>
cd "Gov App with Django"
setup.bat
```

**All Other Users:**
```bash
git clone <your-repo-url>
cd "Gov App with Django"
python setup.py
```

### Option 2: Manual Setup

```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd "Gov App with Django"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp env.example .env
# Edit .env with your settings

# 5. Set up database
python manage.py migrate

# 6. Create admin user
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

## What Each Person Gets

### Fresh Database
- Each person starts with an empty database
- They need to run `python manage.py migrate` to create tables
- They need to create their own superuser account
- Any existing data in your database won't be included

### Environment Variables
- Each person needs their own `.env` file
- The `env.example` file shows what variables are needed
- They should generate their own `SECRET_KEY`
- Database settings can be customized

### Virtual Environment
- Each person creates their own Python virtual environment
- This isolates the project dependencies from their system
- The `requirements.txt` file lists all needed packages

## Files That Are Included

✅ **Included in GitHub:**
- All Python code (models, views, forms)
- Templates and static files
- URL configurations
- Settings files (with environment variable support)
- Requirements file
- Database migrations
- README and documentation

❌ **NOT Included in GitHub:**
- Database files (db.sqlite3)
- Environment files (.env)
- Virtual environment (venv/)
- Uploaded media files
- Log files
- Cache files

## Common Issues and Solutions

### Issue: "Module not found" errors
**Solution:** Make sure you're in the virtual environment and have run `pip install -r requirements.txt`

### Issue: "Database table doesn't exist"
**Solution:** Run `python manage.py migrate` to create the database tables

### Issue: "SECRET_KEY not set"
**Solution:** Create a `.env` file with your SECRET_KEY (use `env.example` as a template)

### Issue: "Permission denied" on Windows
**Solution:** Run PowerShell as Administrator or use the `setup.bat` file

### Issue: "Port 8000 already in use"
**Solution:** Use a different port: `python manage.py runserver 8001`

## Production vs Development

### Development (What you're doing now)
- Uses SQLite database
- DEBUG=True
- Runs on localhost
- No HTTPS required

### Production (When deployed)
- Use PostgreSQL or MySQL
- DEBUG=False
- Proper domain name
- HTTPS required
- Environment variables for secrets

## Next Steps After Setup

1. **Access the application:**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

2. **Create initial data:**
   - Add users through admin panel
   - Create any necessary groups
   - Set up initial projects

3. **Customize for your needs:**
   - Modify templates
   - Add new features
   - Configure email settings

## Support

If you encounter issues:
1. Check the README.md file
2. Look at Django's official documentation
3. Check the console output for error messages
4. Ensure all prerequisites are installed

## Security Notes

- Never commit `.env` files to version control
- Generate a unique SECRET_KEY for each environment
- Use strong passwords for admin accounts
- Keep dependencies updated
- Use HTTPS in production











