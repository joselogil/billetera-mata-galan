# Deployment Guide - PythonAnywhere

This guide will help you deploy the Billetera Mata Galán app to PythonAnywhere so you can access it from any device.

## Prerequisites

1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Free accounts get a subdomain like `your_username.pythonanywhere.com`

## Step-by-Step Deployment

### 1. Upload Your Code to PythonAnywhere

#### Option A: Using Git (Recommended)

1. First, create a Git repository for your project locally:
   ```bash
   cd /home/joselo/personal/gastos_app
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Push to GitHub/GitLab (create a repository first on the platform)
   ```bash
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

3. On PythonAnywhere, open a Bash console and clone your repo:
   ```bash
   git clone YOUR_REPO_URL gastos_app
   cd gastos_app
   ```

#### Option B: Upload Files Manually

1. Go to the "Files" tab in PythonAnywhere
2. Create a new directory: `gastos_app`
3. Upload all your files to this directory

### 2. Install Dependencies

1. Open a Bash console in PythonAnywhere
2. Navigate to your project:
   ```bash
   cd ~/gastos_app
   ```

3. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 gastos_env
   ```

4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Initialize the Database

1. Create the database directory:
   ```bash
   mkdir -p database
   ```

2. Initialize the database:
   ```bash
   python app.py
   ```
   (Press Ctrl+C after it starts to stop it)

   Or run the init_db function:
   ```bash
   python -c "from app import init_db; init_db()"
   ```

### 4. Configure the Web App

1. Go to the "Web" tab in PythonAnywhere
2. Click "Add a new web app"
3. Choose "Manual configuration" (not Django or Flask wizard)
4. Select Python 3.10
5. Click through the wizard

### 5. Configure WSGI File

1. In the Web tab, find the "Code" section
2. Click on the WSGI configuration file link (e.g., `/var/www/your_username_pythonanywhere_com_wsgi.py`)
3. Delete all the content and replace it with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/gastos_app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (IMPORTANT: Change these!)
os.environ['SECRET_KEY'] = 'CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_MINIMUM_32_CHARACTERS'
os.environ['DATABASE_PATH'] = '/home/YOUR_USERNAME/gastos_app/database/gastos.db'

# Import Flask app
from app import app as application
```

4. **IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username
5. **IMPORTANT**: Change the SECRET_KEY to a random string (you can generate one using Python):
   ```python
   import secrets
   secrets.token_hex(32)
   ```

6. Click "Save"

### 6. Configure Virtual Environment

1. Still in the Web tab, find the "Virtualenv" section
2. Enter the path to your virtual environment:
   ```
   /home/YOUR_USERNAME/.virtualenvs/gastos_env
   ```
   (Replace YOUR_USERNAME with your actual username)

### 7. Set Static Files (Optional but Recommended)

In the Web tab, scroll to "Static files" section:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/gastos_app/static/`

### 8. Reload the Web App

1. Scroll to the top of the Web tab
2. Click the big green "Reload" button
3. Your app should now be live at `https://your_username.pythonanywhere.com`

## Creating Your First User

1. Open a Bash console in PythonAnywhere
2. Navigate to your app:
   ```bash
   cd ~/gastos_app
   ```

3. Start Python:
   ```bash
   python
   ```

4. Create a user:
   ```python
   from app import get_db
   from werkzeug.security import generate_password_hash

   db = get_db()
   hashed_password = generate_password_hash('your_password')
   db.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', ('admin', hashed_password))
   db.commit()
   db.close()
   exit()
   ```

## Troubleshooting

### Check Error Logs

If your app doesn't load:
1. Go to the Web tab
2. Scroll down to "Log files"
3. Check the error log for details

### Common Issues

1. **Import errors**: Make sure all dependencies are installed in the virtual environment
2. **Database errors**: Ensure the database directory exists and has proper permissions
3. **404 errors**: Check that your WSGI file is configured correctly
4. **Secret key warnings**: Make sure you changed the SECRET_KEY in the WSGI file

### Database Location

Your database will be at:
```
/home/YOUR_USERNAME/gastos_app/database/gastos.db
```

You can back it up by downloading it from the Files tab.

## Updating Your App

When you make changes:

1. If using Git:
   ```bash
   cd ~/gastos_app
   git pull
   ```

2. If uploading manually: Upload changed files via the Files tab

3. Reload your web app from the Web tab

## Important Security Notes

1. **Change the SECRET_KEY**: Never use the default secret key in production
2. **Use HTTPS**: PythonAnywhere provides HTTPS by default - always access via https://
3. **Backup your database**: Regularly download your database file as a backup
4. **Strong passwords**: Use strong passwords for all user accounts

## Free Account Limitations

- Your app will sleep after 3 months of inactivity
- You get one web app
- Your URL will be `username.pythonanywhere.com`
- To get a custom domain, you need a paid account

## Support

If you encounter issues:
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Forums: https://www.pythonanywhere.com/forums/

---

**Note**: After deployment, you can access your app from any device by visiting `https://your_username.pythonanywhere.com`
