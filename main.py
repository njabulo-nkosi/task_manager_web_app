from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
Bootstrap5(app)


# Create Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# To-Do Form
class TaskForm(FlaskForm):
    name = StringField(label='Task', validators=[DataRequired()])
    time = SelectField(label="Time",
                       choices=['08:00', '09:00', '10:00', '11:00', '12:00', '13:00'], validators=[DataRequired()])
    day = SelectField(label='Day',
                      choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                      validators=[DataRequired()])
    location = SelectField(label='Location',
                           choices=['Office', 'Home Office', 'Other'], validators=[DataRequired()])
    reminder = SelectField(label='Set reminder',
                           choices=['Yes', 'No'], validators=[DataRequired()])
    priority = SelectField(label='Priority',
                           choices=['High', 'Medium', 'Low'], validators=[DataRequired()])
    category = SelectField(label='Category',
                           choices=['Work', 'Personal', 'Errand'], validators=[DataRequired()])
    assigned_to = SelectField(label='Assigned To',
                              choices=['Development team', 'BA team', 'Snr. Management', 'Individual'],
                              validators=[DataRequired()])
    status = SelectField(label='Status',
                         choices=['Not started', 'In progress', 'Completed'],
                         validators=[DataRequired()])
    submit = SubmitField(label='Add Task')


# Create db Table
class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    time: Mapped[str] = mapped_column(String(50), nullable=False)
    day: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    reminder: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_to: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


# with app.app_context():
#     db.create_all()
#     db.init_app(app)

@app.route('/')
def homepage():
    current_year = datetime.datetime.now().year
    return render_template('index.html', current_year=current_year)


@app.route('/all-tasks')
def get_all_tasks():
    current_year = datetime.datetime.now().year

    admin_access = request.args.get('key') == SECRET_KEY
    all_tasks = db.session.execute(db.select(Task)).scalars().all()
    tasks = [task for task in all_tasks]
    return render_template('all_tasks.html', all_tasks=tasks, admin_access=admin_access, current_year=current_year)


@app.route('/task/<int:task_id>')
def show_task(task_id):
    current_year = datetime.datetime.now().year

    requested_task = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
    return render_template("task.html", task=requested_task, current_year=current_year)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    current_year = datetime.datetime.now().year

    form = TaskForm()

    if form.validate_on_submit() and request.method == "POST":
        new_task = Task(
            name=request.form.get('name'),
            time=request.form.get('time'),
            day=request.form.get('day'),
            location=request.form.get('location'),
            reminder=request.form.get('reminder'),
            priority=request.form.get('priority'),
            category=request.form.get('category'),
            assigned_to=request.form.get('assigned_to'),
            status=request.form.get('status'),
        )
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('get_all_tasks'))

    return render_template("add-task.html", form=form, current_year=current_year)


@app.route('/delete-task/<task_id>')
def delete_task(task_id):
    task_to_delete = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()

    db.session.delete(task_to_delete)
    db.session.commit()

    return redirect(url_for('get_all_tasks', task_id=task_to_delete.id))


if __name__ == "__main__":
    app.run(debug=True)
