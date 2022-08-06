from email.policy import default
from django.shortcuts import render
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///virtual.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#データベースの設定
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    detail = db.Column(db.String(100), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)

#ユーザー情報用のデータベースの設定
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    total = db.Column(db.Integer, nullable = False)

#サインアップ
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        total = 0
        user = User(username = username, password = password, total = total)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

#ログイン
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        global username
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if user.password == password:
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

#ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

#ホーム画面
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.start_time).all()
        return render_template('index.html', posts = posts)
    else:
        name = request.form.get('name')
        detail = request.form.get('detail')
        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        date_s = datetime.datetime.now(tokyo_tz).strftime('%Y/%m/%d %H:%M:%S.%f')[:-7]
        start_time = datetime.datetime.strptime(date_s, '%Y/%m/%d %H:%M:%S')
        new_post = Post(name = name, detail = detail, start_time = start_time)

        db.session.add(new_post)
        db.session.commit()

        return redirect('/')

#作成画面
@app.route('/create')
@login_required
def create():
    return render_template('create.html', name = current_user.username)

#終了画面
@app.route('/finish/<int:id>')
@login_required
def read(id):
    post = Post.query.get(id)
    user = current_user

    total = user.total
    tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
    finish_time = datetime.datetime.now(tokyo_tz).strftime('%Y/%m/%d %H:%M:%S.%f')[:-7]
    finish_time = datetime.datetime.strptime(finish_time, '%Y/%m/%d %H:%M:%S')
    start_time = post.start_time
    td = finish_time - start_time
    second = td.total_seconds()
    hour = round(second/3600,2)
    total = total + round(hour,2)
    total =round(total,2)

    userupdate = User.query.get(user.id)
    userupdate.total = total 
        
    db.session.merge(userupdate)
    db.session.commit()

    return render_template('finish.html', post = post, finish_time = finish_time, start_time = start_time, td = td, total = total)

#削除画面
@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)

    db.session.commit()
    return redirect('/')

#マイページ
@app.route('/mypage')
@login_required
def mypage():
    rank = 'Registar'
    if current_user.total>=50:
        rank = 'Begineer'
    elif current_user.total >= 100:
        rank = 'Intermediate'
    elif current_user.total >= 200:
        rank = 'Advanced'
    elif current_user.total >= 300:
        rank = 'Expert'
    elif current_user.total >= 400:
        rank = 'Master'
    elif current_user.total >= 500:
        rank = 'Grandmaster'
    


    return render_template("mypage.html", user = current_user, rank = rank)

if __name__  == '__main__':
    app.run()