"""
WSGI configuration for PythonAnywhere deployment
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/gastos_app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'CHANGE_THIS_TO_A_RANDOM_SECRET_KEY'
os.environ['DATABASE_PATH'] = '/home/YOUR_USERNAME/gastos_app/database/gastos.db'

# Import Flask app
from app import app as application
