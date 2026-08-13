from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint, jsonify)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comment, Like
from flaskblog.posts.forms import PostForm, CommentForm
from flaskblog.utils import abort_if_not_author

posts = Blueprint('posts', __name__)


@posts.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
     form = PostForm()
     if form.validate_on_submit():
         post= Post(title=form.title.data, content=form.content.data, author=current_user)
         db.session.add(post)
         db.session.commit()
         flash('Your post has been created! ', 'success')
         return redirect(url_for('main.home'))
     return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route("/post/<int:post_id>",methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(body=form.content.data, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    # Fix #9: Query comments from DB and pass to template
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments)


@posts.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Added authorization check — only the author can update
    abort_if_not_author(post)
    form = PostForm()
        
    if form.validate_on_submit():
        post.title =  form.title.data
        post.content =  form.content.data
        db.session.commit()
        # Fix #22: Fixed flash category typo 'succces' → 'success'
        flash('Your post has been updated','success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content 

    return render_template('create_post.html', title='update Post', form=form, legend='Update Post')


# Fix #2/#3: Removed broken post_detail route entirely
# It had conflicting URL pattern, variable name collision, and used
# an in-memory dict instead of the database


@posts.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    abort_if_not_author(post)

    db.session.delete(post)
    db.session.commit()

    flash("Your post has been deleted!", "success")
    return redirect(url_for("main.home"))


@posts.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
def like_post(post_id):
    """AJAX endpoint — toggles like on a post and returns updated count."""
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    return jsonify({'liked': liked, 'count': post.like_count})
