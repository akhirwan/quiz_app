from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, bcrypt, Users, Questions
from weather import get_weather
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
import random

load_dotenv()

password = quote_plus(os.getenv('DB_PWD'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{password}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
  db.create_all()

@app.route('/')
def index():
  city = request.args.get('city')
  weather_data = None
  error_message = None
  if city:
    result = get_weather(city)
    if 'error' in result:
      error_message = result['error']
    else:
      weather_data = result['data']
      
  return render_template(
    'index.html', 
    weather=weather_data, 
    error=error_message)

@app.route('/register', methods=['GET','POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    nickname = request.form['nickname']
    
    password = request.form['password']
    confirm = request.form['confirm']    
    if password != confirm:
      flash('Password do not match!')
      return redirect(url_for('register'))
    
    if Users.query.filter_by(username=username).first():
      flash('Username already used!')
      return redirect(url_for('register'))
    
    users = Users(username=username, nickname=nickname)
    users.set_password(password)
    
    db.session.add(users)
    db.session.commit()
    
    flash('Registration is success !')    
    return redirect(url_for('login'))
  
  return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
  
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    users = Users.query.filter_by(username=username).first()
    
    if users and users.check_password(password):
      session['user_id'] = users.id
      return redirect(url_for('quiz'))
    
    flash('Login failed!')
    
  return render_template('login.html')

@app.route('/quiz')
def quiz():
  # User must be logged in
  if 'user_id' not in session:
    return redirect(url_for('login'))
  
  user = Users.query.get(session['user_id'])
  
  # Create a randomized question order ONLY once per session
  if 'question_order' not in session:
    # Fetch all question IDs
    all_ids = [q.id for q in Questions.query.all()]
    
    # If no questions exist, show "no questions" page
    if not all_ids:
      return render_template('no_questions.html')
    
    # Shuffle question order and save into session
    random.shuffle(all_ids)
    session['question_order'] = all_ids
    
    # Set the starting index to 0 (first question)
    session['current_index'] = 0
    
  # Get the saved question order from session
  question_order = session['question_order']
  total_questions = len(question_order)
  
  # Ensure index stays within valid range
  if session['current_index'] < 0:
    session['current_index'] = 0
    
  if session['current_index'] >= total_questions:
    return redirect(url_for('result'))
    
  # Get the question ID based on randomized order
  question_id = question_order[session['current_index']]
  question = Questions.query.get(question_id)
  
  # Render the quiz page with current question and user score
  return render_template(
    'quiz.html',
    question=question,
    index=session['current_index'] + 1,  # for display (1-based)
    total=total_questions,
    score=user.score
  )

@app.route('/next')
def next_question():
  if 'current_index' in session:
    session['current_index'] += 1
  return redirect(url_for('quiz'))

@app.route('/prev')
def prev_question():
  if 'current_index' in session:
    session['current_index'] -= 1
  return redirect(url_for('quiz'))

@app.route('/answer/<int:question_id>', methods=['POST'])
def answer(question_id):
  # if no choosed answer
  selected = request.form.get('option')
  question = Questions.query.get(question_id)
  users = Users.query.get(session['user_id'])
  
  if not selected:
    flash("choose one answer!", "warning")
    # stay in same question
    return redirect(url_for('quiz'))
  
  # if correct, add score
  if selected == question.correct_option:
    users.score += 10
    db.session.commit()
    
  # next question
  current_index = session.get('current_index', 1)
  total = Questions.query.count()
  
  # if available next question
  if current_index < total:
    session['current_index'] = current_index + 1
  else:
    # if all questions answered
    flash("Quiz is done! no more question.", "info")
    return redirect(url_for('result'))
  
  return redirect(url_for('quiz'))

@app.route('/result')
def result():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  
  user = Users.query.get(session['user_id'])
  total_questions = Questions.query.count()
  
  return render_template(
    'result.html',
    score=user.score,
    total=total_questions
  )

@app.route('/restart', methods=['POST'])
def restart_quiz():
  session['current_index'] = 0
  user = Users.query.get(session['user_id'])
  # user.score = 0
  db.session.commit()
  
  return redirect(url_for('quiz'))

@app.route('/leaderboard')
def leaderboard():
  users = Users.query.order_by(Users.score.desc()).all()
  return render_template('leaderboard.html', users=users)

@app.route('/logout')
def logout():
  user = Users.query.get(session['user_id'])
  # user.score = 0
  db.session.commit()
  session.clear()
  return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(debug=True) # default run at port 5000