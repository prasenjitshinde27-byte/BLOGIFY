from flask import (render_template, url_for, flash,  
                   redirect, request, abort, Blueprint, current_app, jsonify)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from flaskblog import db
from flaskblog.models import Post , Comment, Like
from flaskblog.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
     form = PostForm()
     if form.validate_on_submit():
         post= Post(title=form.title.data, content=form.content.data, author=current_user)
         db.session.add(post)
         try:
             db.session.commit()
         except SQLAlchemyError:
             db.session.rollback()
             current_app.logger.exception('Failed to create post for user %s', current_user.id)
             flash('Could not create your post due to a server error. Please try again.', 'danger')
             return render_template('create_post.html', title='New Post', form=form, legend='New Post')
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
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Failed to add comment on post %s', post.id)
            flash('Could not add your comment due to a server error. Please try again.', 'danger')
            return redirect(url_for('posts.post', post_id=post.id))
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
    if post.author != current_user:
        abort(403)
    form = PostForm()
        
    if form.validate_on_submit():
        post.title =  form.title.data
        post.content =  form.content.data
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception('Failed to update post %s', post.id)
            flash('Could not update your post due to a server error. Please try again.', 'danger')
            return render_template('create_post.html', title='update Post', form=form, legend='Update Post')
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

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception('Failed to delete post %s', post.id)
        flash('Could not delete your post due to a server error. Please try again.', 'danger')
        return redirect(url_for('posts.post', post_id=post.id))

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
        liked = False
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post_id))
        liked = True
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception('Failed to toggle like on post %s', post_id)
        return jsonify({'error': 'Could not update like. Please try again.'}), 500
    return jsonify({'liked': liked, 'count': post.like_count})
