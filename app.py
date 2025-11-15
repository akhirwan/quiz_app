from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Users, Questions
from weather import get_weather
from urllib.parse import quote_plus
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

password = quote_plus("@dmiN_123")
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://h_irwan:{password}@localhost/quiz_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
    
    flash('Login gagal!')
    
  return render_template('login.html')

@app.route('/quiz')
def quiz():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  
  # Ambil user
  user = Users.query.get(session['user_id'])
  
  # Ambil semua pertanyaan urut berdasarkan ID paling kecil
  questions = Questions.query.order_by(Questions.id.asc()).all()
  total_questions = len(questions)
  
  if total_questions == 0:
    return render_template('no_questions.html')
  
  # Jika belum ada index dalam session → set ke 1
  if 'current_index' not in session:
    session['current_index'] = 1
    
  # Pastikan index tidak keluar batas
  if session['current_index'] < 1:
    session['current_index'] = 1
    
  if session['current_index'] > total_questions:
    session['current_index'] = total_questions
    
  # Ambil pertanyaan sesuai posisi
  question = questions[session['current_index'] - 1]
  return render_template(
    'quiz.html',
    question=question,
    index=session['current_index'],
    total=total_questions,
    score=user.score
  )

@app.route('/quiz/next')
def quiz_next():
  if 'user_id' not in session:
    return redirect(url_for('login'))

  total = Questions.query.count()

  if session.get('current_index', 1) < total:
    session['current_index'] += 1

  return redirect(url_for('quiz'))

@app.route('/quiz/previous')
def quiz_previous():
  if 'user_id' not in session:
    return redirect(url_for('login'))

  if session.get('current_index', 1) > 1:
    session['current_index'] -= 1

  return redirect(url_for('quiz'))

@app.route('/answer/<int:question_id>', methods=['POST'])
def answer(question_id):
    # Aman: jika user tidak memilih jawaban
    selected = request.form.get('option')

    question = Questions.query.get(question_id)
    users = Users.query.get(session['user_id'])

    # Jika user tidak memilih jawaban
    if not selected:
        flash("Pilih salah satu jawaban sebelum melanjutkan!", "warning")
        # tetap di pertanyaan SAMA
        return redirect(url_for('quiz'))

    # Jika jawaban benar → tambah skor
    if selected == question.correct_option:
        users.score += 10
        db.session.commit()

    # --- PENTING: Selalu pindah ke pertanyaan berikut ---
    current_index = session.get('current_index', 1)
    total = Questions.query.count()

    # Jika masih ada pertanyaan berikutnya
    if current_index < total:
        session['current_index'] = current_index + 1
    else:
        # Jika pertanyaan sudah habis
        flash("Kuis selesai! Tidak ada pertanyaan lagi.", "info")
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
    session['current_index'] = 1
    user = Users.query.get(session['user_id'])
    user.score = 0
    db.session.commit()
    return redirect(url_for('quiz'))

@app.route('/leaderboard')
def leaderboard():
  users = Users.query.order_by(Users.score.desc()).all()
  return render_template('leaderboard.html', users=users)

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(debug=True)
  # app.run(debug=True, port=4040)