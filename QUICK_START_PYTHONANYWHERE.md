# Quick Start - Deploy to PythonAnywhere

Follow these steps to get your app live in under 30 minutes!

## 1. Create PythonAnywhere Account
- Go to https://www.pythonanywhere.com/
- Sign up for a free account
- Your app will be at: `https://YOUR_USERNAME.pythonanywhere.com`

## 2. Upload Your Code

### Easy Way (Upload Files):
1. Click "Files" tab
2. Create directory: `gastos_app`
3. Upload all these files:
   - `app.py`
   - `requirements.txt`
   - `importar_excel.py`
   - All files in `templates/` folder

### Better Way (Using Git):
```bash
# On your local machine first:
cd /home/joselo/personal/gastos_app
git init
git add .
git commit -m "Initial commit"
# Push to GitHub, then on PythonAnywhere:
git clone YOUR_REPO_URL gastos_app
```

## 3. Setup Virtual Environment
Open a Bash console in PythonAnywhere:
```bash
cd ~/gastos_app
mkvirtualenv --python=/usr/bin/python3.10 gastos_env
pip install -r requirements.txt
```

## 4. Initialize Database
```bash
mkdir -p database
python -c "from app import init_db; init_db()"
```

## 5. Configure Web App
1. Go to "Web" tab → "Add a new web app"
2. Choose "Manual configuration" → Python 3.10
3. Set Virtualenv to: `/home/YOUR_USERNAME/.virtualenvs/gastos_env`

## 6. Edit WSGI File
Click on WSGI configuration file, delete everything, paste this:

```python
import sys
import os

project_home = '/home/YOUR_USERNAME/gastos_app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# IMPORTANT: Change these values!
os.environ['SECRET_KEY'] = 'PUT_A_RANDOM_SECRET_KEY_HERE_AT_LEAST_32_CHARS'
os.environ['DATABASE_PATH'] = '/home/YOUR_USERNAME/gastos_app/database/gastos.db'

from app import app as application
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

## 7. Generate Secret Key
In a Bash console:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and use it as your SECRET_KEY in the WSGI file.

## 8. Reload Web App
- Go to Web tab
- Click big green "Reload" button
- Visit: `https://YOUR_USERNAME.pythonanywhere.com`

## 9. Create First User
In a Bash console:
```bash
cd ~/gastos_app
python
```

Then in Python:
```python
from app import get_db
from werkzeug.security import generate_password_hash

db = get_db()
password = generate_password_hash('your_password_here')
db.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', ('admin', password))
db.commit()
db.close()
exit()
```

## 10. Login!
Visit `https://YOUR_USERNAME.pythonanywhere.com` and login with:
- Username: `admin`
- Password: (whatever you set above)

---

## Troubleshooting

**App shows error?**
- Check error log in Web tab → Log files section
- Make sure you replaced YOUR_USERNAME in WSGI file
- Verify virtualenv path is correct

**Can't see the app?**
- Click Reload button in Web tab
- Wait 30 seconds and refresh browser

**Need help?**
- See full guide: `DEPLOYMENT.md`
- PythonAnywhere help: https://help.pythonanywhere.com/

---

That's it! Your app is now accessible from anywhere! 🎉
