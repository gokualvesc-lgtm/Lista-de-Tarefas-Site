from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def register_screen():
    return render_template("register.html")

@app.route("/register/submited", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username:
        return render_template(
        "register.html",
        erro="Digite um nome de usuário!")
    if not password:
        return render_template(
            "register.html",
            erro="Digite uma senha!")
    if len(password) < 6:
        return render_template("register.html", erro="Senha muito pequena! Senha deve conter 6 caracteres!")
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE nome = ?", (username,))
    result = cursor.fetchone()
    if result:
        return render_template("register.html", erro="Usuario ja Cadastrado!")
    cursor.execute("INSERT INTO users (nome, senha) VALUES (?,?)", (username, password))
    conn.commit()
    conn.close()
    return redirect(url_for("login_screen"))


@app.route("/login")
def login_screen():
    return render_template("login.html")

@app.route("/login/submited", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE nome = ? and senha = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        session["username"] = username
        session["user_id"] = result[0]
        return redirect(url_for("user"))
    return render_template("login.html", erro="Usuario ou senha Incorretos!")

@app.route("/user")
def user():
    if not session.get("username"):
        return redirect(url_for("login_screen"))
    return render_template("user.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/user/tasks")
def tasks_screen():
    if not session.get("username"):
        return redirect(url_for("login_screen"))
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],))
    tasks = cursor.fetchall()
    conn.close()
    return render_template("lista_tarefas.html", tasks=tasks, username=session["username"])

@app.route("/user/tasks/add", methods=["POST"])
def task_add():
    if not session.get("username"):
        return redirect(url_for("login_screen"))
    titulo = request.form.get("titulo")
    if not titulo:
        return redirect(url_for("tasks_screen"))
    if len(titulo) > 31:
        return redirect(url_for("tasks_screen"))
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (titulo, user_id) VALUES (?, ?)", (titulo, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks_screen"))

@app.route("/user/tasks/remove", methods=["POST"])
def task_remove():
    if not session.get("username"):
        return redirect(url_for("login_screen"))
    task_id = request.form.get("task_id")
    if not task_id:
        return redirect(url_for("tasks_screen"))
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ? and user_id = ?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks_screen"))

@app.route("/user/tasks/toggle", methods=["POST"])
def task_toggle():
    if not session.get("username"):
        return redirect(url_for("login_screen"))
    task_id = request.form.get("task_id")
    if not task_id:
        return redirect(url_for("tasks_screen"))
    conn = sqlite3.connect("BancoDados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ? and user_id = ?", (task_id, session["user_id"]))
    task = cursor.fetchone()
    if not task:
        conn.close()
        return redirect(url_for("tasks_screen"))
    if task[2] == 0:
        cursor.execute("UPDATE tasks SET concluida = ? WHERE id = ? and user_id = ?", (1, task_id, session["user_id"]))
    else:
        cursor.execute("UPDATE tasks SET concluida = ? WHERE id = ? and user_id = ?", (0, task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("tasks_screen"))

if __name__ == "__main__":
    app.run()