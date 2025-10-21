# Patrick's Governance App for CC ITS

A Django-based project management and governance application for CC ITS (Information Technology Services).

## Features

- Project intake and management
- User authentication and authorization
- Project status tracking
- File uploads and management
- Admin interface for project oversight

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation and Setup

### Quick Setup (Recommended)

For the easiest setup experience, use our automated setup script:

```bash
git clone <your-repository-url>
cd "Gov App with Django"
python setup.py
```

The setup script will automatically:
- Create a virtual environment
- Install all dependencies
- Generate a secure SECRET_KEY
- Create a `.env` file with default settings
- Run database migrations
- Optionally create a superuser account
- Collect static files

### Manual Setup

If you prefer to set up manually or the automated script doesn't work:

#### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Gov App with Django"
```

#### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Copy the example environment file
cp env.example .env
```

Edit the `.env` file with your own values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

**Important:** Generate a new SECRET_KEY for your environment. You can use Django's built-in function:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

#### 5. Database Setup

```bash
python manage.py migrate
```

#### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

#### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Access Points

- **Main Application**: http://127.0.0.1:8000/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **Dashboard**: http://127.0.0.1:8000/dashboard/

## Project Structure

```
Gov App with Django/
├── project_intake/          # Main Django project settings
├── projects/               # Main application
├── templates/              # Global templates
├── static/                 # Static files
├── media/                  # User-uploaded files
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

### Running Tests

```bash
python manage.py test
```

### Making Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files

```bash
python manage.py collectstatic
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your environment variables
2. Use a production database (PostgreSQL recommended)
3. Configure proper `ALLOWED_HOSTS`
4. Set up a production WSGI server (Gunicorn, uWSGI)
5. Use a reverse proxy (Nginx, Apache)
6. Configure HTTPS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For support or questions, please contact [your contact information].
