import hashlib
import os
import uuid
from datetime import datetime
from flask_babel import lazy_gettext as _l

from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from form import LoginForm, RegistrationForm, EditProfileForm, PostForm
from config import user, app, login, db
from flask_login import current_user, login_user, login_required, logout_user
from models import User, Post

login.login_view = 'user.login'

login.login_message = _l('Please log in to access this page.')

UPLOAD_FOLDER = 'static'
# 这条代码用于重定向，当用户没有登陆的情况下，访问index页面，manage.py文件就会根据这条代码将用户
# 重定向到def login() 函数，让用户先进行登陆


# 程序主页
@user.route('/', methods=['GET', 'POST'])
@user.route('/index', methods=['GET', 'POST'])
@login_required  # 如果我没有登陆，就定位到index函数，那么我得登陆，
# 此字段自动加上*/login?next=/index*，用于登陆后重定向到我之前定位的函数，这个next字段会被特定代码段处理，详见login()函数
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)  # author 是post绑定的外键用户对象，用于指定哪位用户发送了此post
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('user.index'))
        # Post/Redirect/Get，从post方式接收用户输入，然后再以get形式重定向到之前页面
        # 防止反复提交插入重复表单数据

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('user.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user.index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home Page', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# 登陆处理函数
@user.route('/login', methods=['GET', 'POST'])
def login():
    """
    当用户在浏览器点击提交按钮后，浏览器会发送`POST`请求。
    `form.validate_on_submit()`就会获取到所有的数据，
    运行字段各自的验证器，全部通过之后就会返回`True`，这表示数据有效。
    :return: 渲染后页面
    """

    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')  # 登陆错误提示信息，在login.html内部进行判断输出处理
            return redirect(url_for('user.login'))

        # login_user() 是flask_login自带的方法，是将登陆用户写入session中，共在session中保存了三个数据：
        # session['user_id'] = user_id
        # session['_fresh'] = fresh
        # session['_id'] = current_app.login_manager._session_identifier_generator()
        # 这三个数据用来确定用户登陆之后的状态，并用于全局确认用户，和前后端共同确认用户
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # request.args.get('next')是通过get方式进行参数传递，next字段是通过@login_required装饰器生成，让登陆之后的用户定位到
        # 登陆之前index页面
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# 登出处理函数
@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.index'))


# 用户注册函数
@user.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('user.login'))
    return render_template('retister.html', title='Register', form=form)


# 用户个人主页函数
@user.route('/users/<username>')  # <username>是动态的，当一个路由包含动态组建时，Flask接受该部分url中任何文本
# 并将以实际文本作为参数调用该视图函数：例如，如果客户端浏览器请求URL `/user/susan`，则视图函数将被调用，
# 其参数`username`被设置为`'susan'`。 因为这个视图函数只能被已登录的用户访问，所以我添加了`@login_required`装饰器。
@login_required  # 将此函数保护起来，未经登陆验证的匿名用户不得访问，会被重定向到登陆页面
def users(username):
    user = User.query.filter_by(username=username).first_or_404()  # first()变种方法，找到则返回结果，没找到返回404 error
    page = request.args.get('page', 1, type=int)
    # page = request.args.get('page', 1, type=int) 'page'是字典中的键， 1指定返回格式，不指定，如果找不到键，返回None，指定1 则返回1
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user.users', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user.users', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template('users.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@user.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():

    print(current_user, '=======================')

    upload_file = request.files.get('img')
    save_file_name = new_file_name(upload_file.content_type)
    save_file_path = os.path.join('/home/storm/PycharmProjects/flask_dog_book/static/upload', save_file_name)

    # with open(save_file_path, 'wb') as f:
    #     for part in upload_file.chunks():
    #         f.write(part)
    #         f.flush()

    upload_file.save(save_file_path)
    msg = '/static/upload/' + save_file_name

    current_user.icon_path = msg
    db.session.commit()
    return msg


def crypt(pwd, cryptName='md5'):
    md5 = hashlib.md5()
    md5.update(pwd.encode())
    return md5.hexdigest()


def new_file_name(contentType):
    fileName = crypt(str(uuid.uuid4()))
    extName = '.jpg'
    if contentType == 'image/png':
        extName = '.png'

    return fileName + extName


@user.route('/del_msg/<username>/<post>')
@login_required
def del_msg(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    if user:
        user.posts.filter_by(body=post).delete()
        db.session.commit()
    return redirect(url_for('user.users', username=username))


# 用户登陆确认函数，用于确定用户最后一次的登陆时间
@app.before_request
def before_request():
    """
    The function will be called without any arguments. If it returns a
        non-None value, the value is handled as if it was the return value from
        the view, and further request handling is stopped.
        所有的请求函数被请求之前调用before_request，并返回一个value，如果value为None，则继续调用此函数，如果value
        不为空，则在下一个函数调用之前就停止调用before_request，确保返回的value是本次登陆时间
    :return:
    """
    if current_user.is_authenticated:  # current_user被调用之后，就已经默认运行了db.session.add(current_user)所以不必重复使用
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# 用户个人状态修改函数
@user.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm(current_user.username)
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        print('=========================')
        return render_template('eidt_profile.html', title='Edit Profile', form=form, user=user)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    print('-------------------------')
    return render_template('eidt_profile.html', title='Edit Profile', form=form, user=user)


# 用户关注函数
@user.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('user.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user.users', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user.users', username=username))


# 用户取消关注函数
@user.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('user.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user.users', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user.users', username=username))


# 用户发现其他用户函数
@user.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('user.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)
















