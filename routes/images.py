import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Image
from config import Config
from routes.auth import current_user

image_bp = Blueprint('images', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@image_bp.route('/')
def home():
    return render_template('home.html')

@image_bp.route('/upload_form', methods=['GET','POST'])
def upload_form():
    user = current_user()
    if not user:
        flash("Please log in to upload images.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        category = request.form['category']
        visibility = request.form.get('visibility', 'public')
        file = request.files['file']

        if not file or not allowed_file(file.filename):
            flash('Invalid file type. Only PNG and JPG allowed.', 'danger')
            return redirect(request.url)

        if file.content_length and file.content_length > Config.MAX_CONTENT_LENGTH:
            flash('File too large. Max 5MB.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        new_image = Image(
            user_id=user.id,
            title=title,
            description=description,
            tags=tags,
            category=category,
            filename=filename,
            visibility=visibility
        )
        db.session.add(new_image)
        db.session.commit()
        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('images.upload_done', image_id=new_image.id))

    return render_template('upload_form.html')

@image_bp.route('/upload_done/<int:image_id>')
def upload_done(image_id):
    image = Image.query.get_or_404(image_id)
    user = current_user()
    return render_template('upload_done.html', image=image, user=user)

@image_bp.route('/edit/<int:image_id>', methods=['GET','POST'])
def edit_image(image_id):
    image = Image.query.get_or_404(image_id)
    user = current_user()
    if not user or image.user_id != user.id:
        flash("You don't have permission to edit this image.", "danger")
        return redirect(url_for('images.explore'))

    if request.method == 'POST':
        image.title = request.form['title']
        image.description = request.form['description']
        image.tags = request.form['tags']
        image.category = request.form['category']
        image.visibility = request.form.get('visibility', image.visibility)
        db.session.commit()
        flash('Image updated!', 'success')
        return redirect(url_for('images.upload_done', image_id=image.id))

    return render_template('upload_form.html', image=image)

@image_bp.route('/delete/<int:image_id>')
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    user = current_user()
    if not user or image.user_id != user.id:
        flash("You don't have permission to delete this image.", "danger")
        return redirect(url_for('images.explore'))

    image.deleted = True
    db.session.commit()
    flash('Image deleted!', 'danger')
    return redirect(url_for('images.explore'))

@image_bp.route('/my_uploads')
def my_uploads():
    user = current_user()
    if not user:
        flash("Please log in to see your uploads.", "danger")
        return redirect(url_for('auth.login'))

    images = Image.query.filter_by(user_id=user.id, deleted=False).order_by(Image.upload_date.desc()).all()
    return render_template('my_uploads.html', images=images)

@image_bp.route('/explore')
def explore():
    search_tag = request.args.get('tag', '').lower()
    sort = request.args.get('sort', 'newest')
    query = Image.query.filter_by(deleted=False, visibility = 'public')

    if search_tag:
        query = query.filter(Image.tags.ilike(f"%{search_tag}%"))

    if sort == 'newest':
        query = query.order_by(Image.upload_date.desc())
    elif sort == 'oldest':
        query = query.order_by(Image.upload_date.asc())

    images = query.all()
    return render_template('explore.html', images=images, search_tag=search_tag, sort=sort)
