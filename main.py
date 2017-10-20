from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogx:blogx@localhost:8889/blogx'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomkey'

#Creates a persistent class to save data to DB. extends(db.Model)= SQL Alchemy plugin 
class Blog (db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User (db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref = 'owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password


#use to check if a string is empty
def is_empty (n): 
        if n == "":
            return True

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route ('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash ("Logged in!", "info")
            return redirect('/newpost')
        else:
            flash ('Username or Password is incorrect', 'error')
            return redirect('/login')
    return render_template('login.html')

@app.route ('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/blog')
        else:
            flash ('Username is taken', 'error')
            return redirect('/signup')        

    return render_template('signup.html')

@app.route ('/logout')
def logout():
    del session['username']
    return redirect ('/blog')

#displays main page with all blog entries
@app.route('/blog', methods = ['POST', 'GET'])
def index(): 
    #captures the blog.id when blog hyperlink is clicked 
    blog_id = request.args.get('id')
    
    #queries for a single blog entry based on blog_id
    single = Blog.query.filter_by(id = blog_id).first()
    
    #queries for logged in user. 
    owner = User.query.filter_by(username=session['username']).first()
    
    #sends user to single view if request.args is present
    if request.args: 
        return render_template('single_view.html', title=single.title, body=single.body)   
    
    #else, takes user to main page
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('blog.html', title="Blog Entry", blogs=blogs)


#displays form for new blog entry
@app.route ('/newpost')
def display_newpost():
    return render_template('newpost.html')

#blog entry data churn
@app.route('/newpost', methods = ['POST'])    #Think about what needs to change here now that we have user sign in. 
def newpost():                                #Will need to incorperate owner_id
    title_name = request.form ['title']
    body_text = request.form ['body']
    owner = User.query.filter_by(username=session['username']).first()
    
    
    #TODO add FLASH validate input fields are not empty
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
        new_blog = Blog(title_name, body_text, owner)
        db.session.add(new_blog)
        db.session.commit()
        
    #take user to single blog view after blog entry
    return redirect('/blog?id='+str(new_blog.id))

if __name__== '__main__':
    app.run()
