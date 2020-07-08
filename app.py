from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'This is a big secret'
bcrypt = Bcrypt(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
  mysql = connectToMySQL('flask_private_wall')
  query = 'SELECT * FROM users WHERE email=%(em)s;'
  data = {'em': request.form.get('email')}
  result = mysql.query_db(query, data)
  if len(result) > 0:
    user = result[0]
    if bcrypt.check_password_hash(user['pw_hash'], request.form.get('pw')):
      session['user_id'] = user['id']
      session['user_fn'] = user['first_name']
      session['user_token'] = bcrypt.generate_password_hash(
        user['email'] + user['last_name'] + str(user['created_at'])
      )
      return redirect('/wall')
  flash('Incorrect email/password.')
  session['postFailure'] = True
  return redirect('/')

@app.route('/register', methods=['POST'])
def register():
  mysql = connectToMySQL('flask_private_wall')
  isEmailTaken = mysql.query_db(
    'SELECT * FROM users WHERE email=%(em)s;',
    {'em': request.form.get('email')}
  )
  session['postFailure'] = isEmailTaken
  if (isEmailTaken):
    flash('Email is taken, use it to login or provide new email.')
  else:
    query = '''
      INSERT INTO users
      (first_name, last_name, email, pw_hash, created_at, updated_at)
      VALUES (%(fn)s, %(ln)s, %(em)s, %(pw_hash)s, NOW(), NOW());
    '''
    data = {
      'fn': request.form.get('first_name'),
      'ln': request.form.get('last_name'),
      'em': request.form.get('email'),
      'pw_hash': bcrypt.generate_password_hash(request.form.get('pw'))
    }
    mysql = connectToMySQL('flask_private_wall')
    mysql.query_db(query, data)
    flash('User account successfully created')
  return redirect('/')

@app.route('/wall')
def wall():
  mysql = connectToMySQL('flask_private_wall')
  users = mysql.query_db('SELECT * FROM users;')
  mysql = connectToMySQL('flask_private_wall')
  messages = mysql.query_db(
    '''
      SELECT messages.id as id, message, messages.created_at, first_name
      FROM messages
      JOIN users ON sender_id=users.id
      WHERE recipient_id=%(id)s;
    ''',
    {'id': session['user_id']}
  )
  for message in messages:
    message['message'] = message['message'].strip()
    time = datetime.now() - message['created_at']
    if time.days > 365:
      message['time_since'] = f'{time.days // 365} years ago'
    elif time.days > 30:
      message['time_since'] = f'{time.days // 30} months ago'
    elif time.days > 0:
      message['time_since'] = f'{time.days} days ago'
    elif time.seconds > 3600:
      message['time_since'] = f'{time.seconds // 3600} hours ago'
    elif time.seconds > 60:
      message['time_since'] = f'{time.seconds // 60} minutes ago'
    elif time.seconds > 0:
      message['time_since'] = f'{time.seconds} seconds ago'
    else:
      message['time_since'] = 'Just now'
  numMessages = len(messages)
  return render_template(
    'wall.html',
    users=users,
    messages=messages,
    numMessages=numMessages
  )

@app.route('/wall/send_message', methods=['POST'])
def send_message():
  mysql = connectToMySQL('flask_private_wall')
  query = '''
    INSERT INTO messages
    (recipient_id, sender_id, message, created_at, updated_at)
    VALUES (%(rid)s, %(sid)s, %(m)s, NOW(), NOW());
  '''
  data = {
    'sid': int(session['user_id']),
    'rid': request.form.get('recipient'),
    'm': request.form.get('message')
  }
  mysql.query_db(query, data)
  flash('Message sent!')
  return redirect('/wall')

@app.route('/wall/delete/<message_id>')
def delete_message(message_id):
  message_id = int(message_id)
  mysql = connectToMySQL('flask_private_wall')
  result = mysql.query_db(
    '''
      SELECT users.id as id, last_name, email, users.created_at FROM messages
      JOIN users ON messages.recipient_id=users.id
      WHERE messages.id=%(id)s;
    ''',
    {'id': message_id}
  )
  user = result[0]
  isOwner = bcrypt.check_password_hash(
    session['user_token'],
    user['email'] + user['last_name'] + str(user['created_at'])
  )
  if isOwner:
    mysql = connectToMySQL('flask_private_wall')
    mysql.query_db(
      'DELETE FROM messages WHERE id=%(id)s;',
      {'id': message_id}
    )
    return redirect('/wall')
  else:
    session['message_id'] = message_id
    return redirect('/danger')

@app.route('/danger')
def danger():
  message_id = session['message_id']
  ip = request.remote_addr
  if 'bad_request' in session:
    return redirect('logout')
  else:
    session['bad_request'] = True
    return render_template('danger.html', message_id=message_id, ip=ip)

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

if (__name__ == '__main__'):
  app.run(debug=True)
