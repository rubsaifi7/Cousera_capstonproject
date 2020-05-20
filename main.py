from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import pymysql
pymysql.install_as_MySQLdb()

with open('config.json','r') as c:
    params=json.load(c)["params"]

local_server=True
app = Flask(__name__)
app.secret_key = 'super secret-key'
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date= db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Postss(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    Content = db.Column(db.String(120), nullable=False)
    date= db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(20), nullable=False)
    subtitle = db.Column(db.String(20), nullable=False)

@app.route("/")
def home():
    pos=Postss.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html',params=params,pos=pos)


@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']==params['admin_user']):
        posts = Postss.query.all()
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('Pass')
        if(username == params["admin_user"] and userpass == params["admin_password"]):
            session['user'] = username
            posts = Postss.query.all()
            return render_template('dashboard.html',params=params,posts=posts)


    #REDIRECT TO ADMIN PANEL
    return render_template('login.html',params=params)

@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
    post = Postss.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params, post=post)

@app.route("/edit/<string:sno>",methods=["GET","POST"])
def edit(sno):
    if ('user' in session and session['user']==params['admin_user']):
        if request.method == "POST":
            box_title=request.form.get('Title')
            Subtitle=request.form.get('subtitle')
            slu= request.form.get('slug')
            Content=request.form.get('Content')
            img = request.form.get('img_file ')
            date=datetime.now()

            if sno =='0':
                poss = Postss(Title=box_title ,subtitle=Subtitle, Content=Content, slug=slu, date=date,img_file=img)
                db.session.add(poss)
                db.session.commit()
            else:
                poss=Postss.query.filter_by(sno=sno).first()
                poss.Title=box_title
                poss.slug=slu
                poss.Content=Content
                poss.subtitle=Subtitle
                poss.img_file=img
                poss.date=date
                db.session.commit()
                return redirect('/edit'+sno)
        poss = Postss.query.filter_by(sno=sno).first()

        return render_template('edit.html',params=params,poss=poss)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_no = phone, message = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


app.run(debug=True)