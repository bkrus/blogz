from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomkey'

class Blog (db.Model): #Creates a persistent class to save data to DB. extends(db.Model)= SQL Alchemy plugin 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods = ['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    #completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()
    return render_template('blog.html', title="Blog Entry", blogs=blogs)

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_name = request.form ['title']
        body_text = request.form['body']
        new_blog = Blog(title_name, body_text)
        db.session.add(new_blog)
        db.session.commit()
    
    return render_template('newpost.html')




if __name__== '__main__':
    app.run()
