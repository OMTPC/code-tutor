# 🐍 Code Tutor - Interactive Python Learning Platform
Code Tutor is a web-based platform designed to teach Python programming to beginners through engaging, interactive exercises and real-world applications. The platform also includes the "Future You" feature, which guides learners towards potential career paths and projects that apply the skills they have acquired.

---

🚀 **Features**

**Modular Learning Path:**
Progress through structured modules, including:

    - Variables & Data Types
    - Control Flow
    - Functions
    - And more...

**Interactive Exercises:**
Complete practical coding challenges with instant feedback.

**"Future You" Section:**
Visualise your career potential and unlock project-based learning as you progress.

**User Authentication:**
Register and log in to track your progress.

**Real-World Relevance:**
Apply Python concepts to hands-on projects and see how they translate into industry applications.

---

🛠️ **Tech Stack**

- **Backend:** Python, Flask, SQLAlchemy, Alembic (for database migrations)
- **Frontend:** HTML, CSS (Bootstrap), JavaScript
- **Authentication:** Flask-Login
- **Regex Matching:** For flexible solution validation
- **Database:** SQLite
- **Deployment:** Flask web server

---

📝 **Installation**

Clone the repository:
```bash
git clone https://github.com/OMTPC/CODE-TUTOR.git
cd CODE-TUTOR
```

Set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up environment variables:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
```

Database Migrations:
```bash
flask db upgrade
```

Populate the database:
```bash
python populate_db.py
python exercise_populate_db.py
```

Run the application:
```bash
flask run
```

The application will be available at: http://127.0.0.1:5000/

💡 **Usage**

- Open your web browser and navigate to http://127.0.0.1:5000/.
- Register or log in to start learning Python.
- Explore the "Future You" section to see career paths and projects that match your progress.
- Track your learning journey through interactive modules.

---

🧑‍💻 **Contributing**

Contributions are welcome!

Feel free to fork the project, create a branch, make your changes, and submit a pull request.

---

🔧 **Troubleshooting**

If the database fails to initialise, ensure your environment variables are correctly set and that you are running the application within the virtual environment.

If you encounter any missing packages, try reinstalling them using:
```bash
pip install -r requirements.txt
```
---

📄 **License**

This project is licensed under the MIT License. See LICENSE for more details.

---

💌 **Contact**

For questions or suggestions, feel free to reach out at:

📧 orlandocaetanouk@gmail.com
