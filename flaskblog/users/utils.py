import os
import secrets 
from PIL import Image, UnidentifiedImageError
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Process and persist the new picture first. If the upload is not a valid
    # image, this raises before we touch the existing avatar.
    output_size = (125, 125)
    try:
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    except UnidentifiedImageError as exc:
        raise OSError('Uploaded file is not a valid image') from exc

    # Only after the new picture is safely saved do we remove the old one, so a
    # failed upload never leaves the user without an avatar.
    from flask_login import current_user
    if current_user.image_file != 'default.jpg':
        old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(old_picture_path):
            try:
                os.remove(old_picture_path)
            except OSError:
                current_app.logger.warning('Could not remove old profile picture: %s', old_picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    sender = current_app.config.get('MAIL_USERNAME') or 'noreply@blogify.com'
    msg = Message(
        'Password Reset Request',
        sender=sender,
        recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:

{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
"""
    mail.send(msg)