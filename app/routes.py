# All routes for app called here
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

# Home
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
	# Post Form
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))

	# Posts & Pagination
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False
	)
	next_url = url_for('index', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Home', posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	# Authenticate user
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Submit
	form = LoginForm()
	# Log in User
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)

		# After User is logged in, redirect to index using next
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(url_for('index'))

	return render_template('login.html', title="Sign In", form=form)

# Logout
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
	# Handling for if authenicated user goes to register page
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Create form, form processing
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)

# User profile
@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False
	)
	next_url = url_for('user', username=user.username, page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

# User last visit
# Before anything is processed, get the date now of current user activity
@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

# Edit User Profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	# On form submit
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved')
		return redirect(url_for('edit_profile'))

	# Otherwise, return the data and render it to edit_profile.html
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)

# Follow
@app.route('/follow/<username>')
@login_required
def follow(username):
	# Look for username
	user = User.query.filter_by(username=username).first()

	# Checks
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user', username=username))

	# Follow user
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('user', username=username))

# Unfollow
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	# Look for username
	user = User.query.filter_by(username=username).first()

	# Checks
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('user', username=username))

	# Unfollow user
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}'.format(username))
	return redirect(url_for('user', username=username))

# Explore
@app.route('/explore')
@login_required
def explore():
	# Posts & Pagination
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False
	)
	next_url = url_for('explore', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)
