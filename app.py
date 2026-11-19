
from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, get_db_connection
from datetime import date, timedelta

app = Flask(__name__)

create_tables()




@app.route("/")
def dashboard():
    conn = get_db_connection()

    today = date.today().isoformat()

    # Today's expenses
    today_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date = ?",
        (today,)
    ).fetchone()[0]

    # Total tasks
    total_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    # Completed tasks
    completed_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
    ).fetchone()[0]

    # Today's study hours
    study_hours = conn.execute(
        "SELECT COALESCE(SUM(duration), 0) FROM study_sessions WHERE session_date = ?",
        (today,)
    ).fetchone()[0]
    # Total habits
    total_habits = conn.execute(
    "SELECT COUNT(*) FROM habits"
).fetchone()[0]

    # Habits completed today
    completed_habits = conn.execute(
    "SELECT COUNT(*) FROM habit_logs WHERE log_date = ? AND completed = 1",
    (today,)
).fetchone()[0]

    # Habit completion percentage
    habit_percentage = (
    (completed_habits / total_habits) * 100
    if total_habits > 0 else 0
)
    # Task score (40 points)
    task_score = (
    (completed_tasks / total_tasks) * 40
    if total_tasks > 0 else 0
)

    # Study score (30 points)
    study_score = min((study_hours / 2) * 30, 30)

    # Habit score (30 points)
    habit_score = (habit_percentage / 100) * 30

    # Total Life Score
    life_score = round(
    task_score + study_score + habit_score
)
    conn.close()

    return render_template(
        "dashboard.html",
        today_expenses=today_expenses,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        study_hours=study_hours,
        total_habits=total_habits,
        completed_habits=completed_habits,
        habit_percentage=habit_percentage,
        life_score=life_score
    )




@app.route("/tasks")
def tasks():
    conn = get_db_connection()
    all_tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("tasks.html", tasks=all_tasks)


@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form["title"]
    category = request.form["category"]
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO tasks (title, category, priority, due_date)
        VALUES (?, ?, ?, ?)
    """, (title, category, priority, due_date))

    conn.commit()
    conn.close()

    return redirect(url_for("tasks"))


@app.route("/complete_task/<int:task_id>")
def complete_task(task_id):
    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("tasks"))


@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("tasks"))


@app.route("/expenses")
def expenses():
    conn = get_db_connection()

    all_expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "expenses.html",
        expenses=all_expenses,
        total=total
    )


@app.route("/add_expense", methods=["POST"])
def add_expense():
    title = request.form["title"]
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO expenses (title, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (title, amount, category, date))

    conn.commit()
    conn.close()

    return redirect(url_for("expenses"))


@app.route("/delete_expense/<int:expense_id>")
def delete_expense(expense_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("expenses"))

@app.route("/study")
def study():
    conn = get_db_connection()

    subjects = conn.execute(
        "SELECT * FROM subjects ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("study.html", subjects=subjects)


@app.route("/add_subject", methods=["POST"])
def add_subject():
    subject_name = request.form["subject_name"]
    total_topics = request.form["total_topics"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO subjects (subject_name, total_topics)
        VALUES (?, ?)
    """, (subject_name, total_topics))

    conn.commit()
    conn.close()

    return redirect(url_for("study"))


@app.route("/update_subject/<int:subject_id>", methods=["POST"])
def update_subject(subject_id):
    completed_topics = request.form["completed_topics"]

    conn = get_db_connection()

    conn.execute("""
        UPDATE subjects
        SET completed_topics = ?
        WHERE id = ?
    """, (completed_topics, subject_id))

    conn.commit()
    conn.close()

    return redirect(url_for("study"))


@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM subjects WHERE id = ?",
        (subject_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("study"))

@app.route("/add_study_session", methods=["POST"])
def add_study_session():
    subject_id = request.form["subject_id"]
    duration = request.form["duration"]
    session_date = request.form["session_date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO study_sessions
        (subject_id, duration, session_date)
        VALUES (?, ?, ?)
    """, (subject_id, duration, session_date))

    conn.commit()
    conn.close()

    return redirect(url_for("study"))

@app.route("/habits")
def habits():
    conn = get_db_connection()

    today = date.today().isoformat()

    all_habits = conn.execute("""
        SELECT h.*,
        COALESCE(l.completed, 0) AS completed_today
        FROM habits h
        LEFT JOIN habit_logs l
        ON h.id = l.habit_id AND l.log_date = ?
        ORDER BY h.id DESC
    """, (today,)).fetchall()

    conn.close()

    return render_template("habits.html", habits=all_habits)


@app.route("/add_habit", methods=["POST"])
def add_habit():
    habit_name = request.form["habit_name"]
    frequency = request.form["frequency"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO habits (habit_name, frequency)
        VALUES (?, ?)
    """, (habit_name, frequency))

    conn.commit()
    conn.close()

    return redirect(url_for("habits"))


@app.route("/complete_habit/<int:habit_id>", methods=["POST"])
def complete_habit(habit_id):
    conn = get_db_connection()

    today = date.today().isoformat()

    existing = conn.execute("""
        SELECT id FROM habit_logs
        WHERE habit_id = ? AND log_date = ?
    """, (habit_id, today)).fetchone()

    if existing:
        conn.execute("""
            UPDATE habit_logs
            SET completed = 1
            WHERE habit_id = ? AND log_date = ?
        """, (habit_id, today))
    else:
        conn.execute("""
            INSERT INTO habit_logs (habit_id, log_date, completed)
            VALUES (?, ?, 1)
        """, (habit_id, today))

    conn.commit()
    conn.close()

    return redirect(url_for("habits"))


@app.route("/delete_habit/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM habit_logs WHERE habit_id = ?",
        (habit_id,)
    )

    conn.execute(
        "DELETE FROM habits WHERE id = ?",
        (habit_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("habits"))
@app.route("/analytics")
def analytics():
    conn = get_db_connection()
    today = date.today().isoformat()

    today_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date = ?",
        (today,)
    ).fetchone()[0]

    total_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    completed_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
    ).fetchone()[0]

    study_hours = conn.execute(
        "SELECT COALESCE(SUM(duration), 0) FROM study_sessions WHERE session_date = ?",
        (today,)
    ).fetchone()[0]

    # Total habits
    total_habits = conn.execute(
        "SELECT COUNT(*) FROM habits"
    ).fetchone()[0]

    # Habits completed today
    completed_habits = conn.execute(
        "SELECT COUNT(*) FROM habit_logs WHERE log_date = ? AND completed = 1",
        (today,)
    ).fetchone()[0]

    # Habit completion percentage
    habit_percentage = (
        (completed_habits / total_habits) * 100
        if total_habits > 0 else 0
    )

    # Task statistics
    task_stats = conn.execute("""
        SELECT status, COUNT(*)
        FROM tasks
        GROUP BY status
    """).fetchall()

    task_labels = [row[0] for row in task_stats]
    task_values = [row[1] for row in task_stats]

    # Expense statistics by category
    expense_stats = conn.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """).fetchall()

    expense_labels = [row[0] for row in expense_stats]
    expense_values = [row[1] for row in expense_stats]

    # Study hours for the last 7 days
    today = date.today()
    start_date = (today - timedelta(days=6)).isoformat()

    study_stats = conn.execute("""
        SELECT session_date, SUM(duration)
        FROM study_sessions
        WHERE session_date BETWEEN ? AND ?
        GROUP BY session_date
        ORDER BY session_date
    """, (start_date, today.isoformat())).fetchall()

    study_labels = [row[0] for row in study_stats]
    study_values = [row[1] for row in study_stats]
    # Habit completion statistics for the last 7 days
    habit_stats = conn.execute("""
    SELECT log_date, COUNT(*)
    FROM habit_logs
    WHERE log_date BETWEEN ? AND ?
    AND completed = 1
    GROUP BY log_date
    ORDER BY log_date
""", (start_date, today.isoformat())).fetchall()

    habit_labels = [row[0] for row in habit_stats]
    habit_values = [row[1] for row in habit_stats]

    conn.close()

    return render_template(
        "analytics.html",
        task_labels=task_labels,
        task_values=task_values,
        expense_labels=expense_labels,
        expense_values=expense_values,
        study_labels=study_labels,
        study_values=study_values,
        today_expenses=today_expenses,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        study_hours=study_hours,
        total_habits=total_habits,
        completed_habits=completed_habits,
        habit_percentage=habit_percentage,
        habit_labels=habit_labels,
        habit_values=habit_values
    )
if __name__ == "__main__":
    app.run(debug=True)
