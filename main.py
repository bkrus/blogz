from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomkey'

#Creates a persistent class to save data to DB. extends(db.Model)= SQL Alchemy plugin 
class Blog (db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#variable to query: select * from Blog, used downstream
blogs = Blog.query.all()

#use to check if a string is empty
def is_empty (n): 
        if n == "":
            return True

#displays main page with all blog entries
@app.route('/blog', methods = ['POST', 'GET'])
def index(): 
    blogs = Blog.query.all()
    return render_template('blog.html', title="Blog Entry", blogs=blogs)

#displays form for new blog entry
@app.route ('/newpost')
def display_newpost():
    return render_template('newpost.html')

#blog entry data churn
@app.route('/newpost', methods = ['POST'])
def newpost():
    title_name = request.form ['title']
    title_error = ''
    
    body_text = request.form ['body']
    body_error = ''
    
    #validate input fields are not empty
    if is_empty(title_name): 
        title_error = 'Title cannot be empty'

    if is_empty(body_text): 
        body_error = 'Body cannot be empty'
        
        #render page with error messages
        return render_template('newpost.html', 
                            title = "New Entry", 
                            body_error=body_error, 
                            title_error=title_error)
        
    #if no errors, save to the DB
    else:
        new_blog = Blog(title_name, body_text)
        db.session.add(new_blog)
        db.session.commit()
        
    #take user back to main page with new blog entry
    return render_template('blog.html', title="Blog Entry", blogs=blogs)

@app.route ('/single_view')
def single_entry():
    return render_template('single_view.html')   


if __name__== '__main__':
    app.run()
