from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "abc"



#class Blogs, makes instances of the title and content persistent in the database
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(46))
    content = db.Column(db.String(140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner


    #TODO what would happen if I moved the helper function outside of the class?
    def is_valid(self):
        if self.title and self.content:
            return True
        else:
            return False

#User class, database needs to store username and password and link to the blogs via owner they have created ()
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(46), unique=True)
    password = db.Column(db.String(22))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


#makes sure user is logged in before creating posts
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blogs' , 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#homepage
@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()

    return render_template('index.html',
                            title="BLOG",
                            users=users
                            )

#filters by user or id
@app.route('/blogs', methods=['POST', 'GET'])
def blogs():

    blog_id = request.args.get('id')
    if (blog_id):
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_template.html', blogs=blogs)

    user_name = request.args.get('username')
    user_id = request.args.get('user')
    if (user_id):
        blogs = Blog.query.filter_by(owner_id=user_id)
        return render_template('single_user.html', blogs=blogs, user_name=user_name)

    blogs = Blog.query.all()
    return render_template('blogs.html',
                            title='BLOG',
                            blogs=blogs,
                            )

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_info = User.query.filter_by(username=username).first()

        if login_info and login_info.password == password:
            session['username'] = username
            flash(username + 'is currently logged on')
            return redirect('/new_post')
        else:
            flash('Incorrect, please try again')

    return render_template('login.html')


#logout route
@app.route('/logout')
def logout():
    username = str(session['username'])
    del session ['username']
    flash(username + 'has been logged out')
    return redirect('/')


#register page to set up a user account (U is the only vowel you dont us "an" instaed of "a" in front of, weird)
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #check to make sure form isnt blank, flash message if it is
        if username == '' or password == '' or verify == '':
            flash('You did not fill out all of the fields or your passwords did not match, please try again :)')
            return render_template('register.html', username=username)

        if password != verify:
            flash('Your passwords dont match, please try again :)')
            return render_template('register.html', username=username)


        #if user is registered create variable to check
        existing_user = User.query.filter_by(username=username).first()

        #username does and does not exist (existense is strange concept)
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = username
            flash('Registered User')
            return redirect('/new_post')
        else:
            flash('You have previously registered this login/password, this is a class project so good luck getting ahold of somebody who can help')

    return render_template('register.html')




#creates a new blogPost and redirects to main page
@app.route('/new_post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':

        blog_name = request.form['blog']
        blog_content = request.form['content']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_name, blog_content, owner)

        if new_blog.is_valid():
            db.session.add(new_blog)
            db.session.commit()
            url = '/blogs?id=' + str(new_blog.id)
            return redirect(url)
        else:
            flash('You need a title and a post to make a blog, please try again')

            return render_template('new_post.html',
                                    category='error',
                                    blog_name=blog_name,
                                    blog_content=blog_content
                                    )

    else:
        return render_template('new_post.html')





if __name__ == "__main__":
    app.run()
