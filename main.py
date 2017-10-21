from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogx:blogx@localhost:8889/blogx'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomkey'

class Blog (db.Model): #Creates a persistent class to save data to DB. extends(db.Model)= SQL Alchemy plugin 

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

def is_empty (n): #use to check if a string is empty
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
        if is_empty(username):
            flash ('Username cannot be empty', 'error')
            return redirect('/signup')
        if len(username) < 3:
            flash ('Username must be greater then 3 characters', 'error')
            return redirect('/signup')
        if is_empty(password):
            flash ('Password cannot be empty', 'error')
            return redirect('/signup')
        if len(password) < 3:
            flash ('Password must be greater then 3 characters', 'error')
            return redirect('/signup')
        if password != verify:
            flash ('Password and Verify do not match', 'error')
            return redirect('/signup')
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Congratulations, you are now registered', 'info')
            return redirect ('/newpost')
        else:
            flash ('Username is taken', 'error')
            return redirect('/signup')        

    return render_template('signup.html')

@app.route ('/logout')
def logout():
    del session['username']
    return redirect ('/blog')


@app.route('/', methods = ['POST', 'GET'])
def home():

    users = User.query.all()
    return render_template('index.html', title="Home", users=users)
    

@app.route('/blog', methods = ['POST', 'GET']) #displays main page with all blog entries
def index(): 
    
    user_id = request.args.get('user') #captures user ID
    blog_id = request.args.get('id') #captures the blog.id when blog hyperlink is clicked 
    
    users = User.query.all()
    userblogs = Blog.query.filter_by(owner_id = user_id).all()
    single = Blog.query.filter_by(id = blog_id).first() #queries for a single blog entry based on blog_id
   
    
    if request.args.get('user'):
        return render_template ('userpage.html', userblogs=userblogs)
    
    if request.args.get('id'):   #sends user to single view if request.args is present
        return render_template('single_view.html', title=single.title, body=single.body)   
    
    blogs = Blog.query.all()
    return render_template('blog.html', title="Blog Entry", blogs=blogs, users=users, userblogs=userblogs)

@app.route ('/newpost') #displays form for new blog entry
def display_newpost():
    return render_template('newpost.html')

#blog entry data churns
@app.route('/newpost', methods = ['POST'])
def newpost():                                
    title_name = request.form ['title']
    body_text = request.form ['body']
    owner = User.query.filter_by(username=session['username']).first()
    
    
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
