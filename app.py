from flask import Flask, render_template, request, redirect, session
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'This is a big secret'

@app.route('/')
def index():
  # mysql = connectToMySQL('first_flask')
  return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
  session['user_fn'] = 'Justin'
  session['user_id'] = 1
  return redirect('/wall')

@app.route('/register', methods=['POST'])
def register():
  return redirect('/wall')

@app.route('/wall')
def wall():
  users = [
    {'id': 1, 'first_name': 'Justin'},
    {'id': 2, 'first_name': 'Lili'},
    {'id': 3, 'first_name': 'Andres'}
  ]
  return render_template('wall.html', users=users)

@app.route('/send_message')
def send_message():
  return redirect('/wall')

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

if (__name__ == '__main__'):
  app.run(debug=True)
