from flask import Flask, redirect, url_for, request, render_template, flash, session
from celery import Celery
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.secret_key = 'hello'
app.config['UPLOAD_FOLDER'] = os.getcwd()+"/uploads"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nnd58xe@gmail.com'
app.config['MAIL_PASSWORD'] = 'nnd020895'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config.update(
    CELERY_BROKER_URL='pyamqp://guest@localhost//',
	CELERY_RESULT_BACKEND='rpc://'
)
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
celery = make_celery(app)

@celery.task
def sendmail():
	with open('./uploads/lists.txt') as email_file:
		email_list = email_file.read().splitlines()
	with open('./uploads/content.txt') as content_file:
		content = content_file.read()
	for email in email_list:
		msg = Message("Hi %s" % email,
				sender='nnd58xe@gmail.com',
				recipients= email_list
				)
		msg.body = content
		mail.send(msg)
	
	return "sent"

@app.route('/sendmail')
def send():
	return sendmail()

@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		password = session['password']
		return 'Logged in as ' + username + '<br>' + \
         "<b><a href = '/logout'>click here to log out</a></b>"
	return "You are not logged in <br><a href = '/login'></b>" + \
"click here to log in</b></a>"

@app.route('/login', methods= ['POST', 'GET'])
def login():
	if request.method == 'POST':
		if request.form['username'] in ["nnd58xe@gmail.com"]:
			session['username'] = request.form['username']
			session['password'] = request.form['password']
			flash("You are login succesful")
			return redirect(url_for('prepare_upload'))
		else:
			return redirect(url_for('index'))


	return '''
		<form action = "http://localhost:5000/login" method = "POST">
			<p>email: <input type = "text" name = "username" /></p>
			<p>password: <input type = "text" name = "password" /></p>
			<p><input type = "submit" value = "submit" /></p>
		</form>

   '''
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))


@app.route('/prepare_upload')
def prepare_upload():
	return "Upload? <br><a href = '/upload'></b>" + \
"Email list file</b></a> \
<br><a href = '/upload'></b>" + \
"Content file</b></a> \
<br><a href = '/sendmail'></b>" + \
"Execute </b></a> "


@app.route('/upload')
def upload():
	return render_template('upload.html')

@app.route('/uploader', methods = ['POST', 'GET'])
def upload_file():
	if request.method == "POST":
		f = request.files['file']
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
		flash("file uploaded successfully")
	return redirect('prepare_upload')

if __name__ == "__main__":
	app.run(debug=True)
