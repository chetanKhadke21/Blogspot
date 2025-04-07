from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from blogspot import db
from blogspot.models import Post, User
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/")
@login_required
@admin_required
def admin_panel():
    status = request.args.get('status', 'all')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    
    query = Post.query
    
    if status == 'approved':
        query = query.filter_by(approved=True)
    elif status == 'unapproved':
        query = query.filter_by(approved=False)
    
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    
    posts = query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    
    stats = {
        'users': User.query.count(),
        'total_posts': Post.query.count(),
        'approved_posts': Post.query.filter_by(approved=True).count(),
        'pending_posts': Post.query.filter_by(approved=False).count()
    }
    
    return render_template('admin/panel.html', posts=posts, stats=stats)

@admin.route("/post/<int:post_id>/approve", methods=['POST'])
@login_required
@admin_required
def approve_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.approved = True
    db.session.commit()
    flash('Post has been approved!', 'success')
    return redirect(url_for('admin.admin_panel'))
