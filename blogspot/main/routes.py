from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, current_app
from flask_login import login_required, current_user
from blogspot import db
from blogspot.models import Post, User, Comment, Like, Image
from blogspot.main.forms import PostForm, CommentForm
import os
from werkzeug.utils import secure_filename
from sqlalchemy import desc, func

main = Blueprint('main', __name__)

@main.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    category = request.args.get('category')
    
    query = Post.query.filter_by(approved=True)
    
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    if category:
        query = query.filter_by(category=category)
    
    posts = query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    categories = ['entertainment', 'food', 'lifestyle', 'travel', 'technology', 'sports']
    return render_template('main/home.html', posts=posts, categories=categories)

@main.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=form.content.data,
            post=post,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.post', post_id=post.id))
    
    return render_template('main/post.html', post=post, form=form)

@main.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author=current_user,
            approved=not current_app.config['REQUIRE_APPROVAL']
        )
        db.session.add(post)
        db.session.commit()
        
        if form.images.data:
            for image_file in form.images.data:
                if image_file.filename:
                    filename = secure_filename(image_file.filename)
                    image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    image = Image(filename=filename, post=post)
                    db.session.add(image)
            db.session.commit()
        
        flash('Your post has been created! It will be visible after approval.', 'success')
        return redirect(url_for('main.home'))
    return render_template('main/create_post.html', form=form)

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('main.post', post_id=post.id))
    
    # Delete associated images from filesystem
    for image in post.images:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename))
        except:
            pass
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@main.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user=current_user, post=post).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'likes': len(post.likes), 'liked': False})
    else:
        like = Like(user=current_user, post=post)
        db.session.add(like)
        db.session.commit()
        return jsonify({'likes': len(post.likes), 'liked': True})

@main.route("/trending")
def trending():
    page = request.args.get('page', 1, type=int)
    
    # Get approved posts ordered by number of likes
    posts = Post.query.filter_by(approved=True)\
        .outerjoin(Like)\
        .group_by(Post.id)\
        .order_by(func.count(Like.id).desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('main/trending.html', posts=posts)

@main.route("/post/<int:post_id>/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(post_id)
    
    if comment.author != current_user and post.author != current_user and not current_user.is_admin:
        flash('You do not have permission to delete this comment.', 'danger')
        return redirect(url_for('main.post', post_id=post_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('main.post', post_id=post_id))

@main.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('main/user_posts.html', posts=posts, user=user)

@main.route("/post/<int:post_id>/comment", methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
        
    comment = Comment(
        content=content,
        post=post,
        author=current_user
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'author': comment.author.username,
        'date': comment.date_posted.strftime('%Y-%m-%d %H:%M'),
        'can_delete': True
    })

@main.route("/post/<int:post_id>/comments", methods=['GET'])
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = []
    for comment in post.comments:
        can_delete = False
        if current_user.is_authenticated:
            can_delete = (comment.author == current_user or 
                         post.author == current_user or 
                         current_user.is_admin)
        comments.append({
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'date': comment.date_posted.strftime('%Y-%m-%d %H:%M'),
            'can_delete': can_delete
        })
    return jsonify(comments)

@main.route("/profile")
@login_required
def profile():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    comments = Comment.query.filter_by(author=current_user).order_by(Comment.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('main/profile.html', posts=posts, comments=comments)
