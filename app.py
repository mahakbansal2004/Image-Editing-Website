from flask import Flask, render_template, request, send_file, flash, redirect, url_for,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os
import io
import imgkit
from werkzeug.utils import secure_filename
#import subprocess
import traceback
#import face_recognition
import random
import string
#from watermark import add_watermark




app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for flashing messages

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


#@app.route('/users')
#def view_users():
 #   users = User.query.all()
  #  return render_template('view_users.html', users=users)


@app.route('/premium', methods=['GET', 'POST'])
def premium():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Create a new User object
        new_user = User(name=name, email=email, password=password)
        
        # Add the new user to the database session
        db.session.add(new_user)
        
        # Commit changes to the database
        db.session.commit()
        
        # Optionally, you can redirect to a success page
        return render_template('success.html', name=name)
    else:
        # Render the premium upgrade form
        return render_template('premium.html')

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
# Add PremiumUpgrade model to Flask-Admin
admin.add_view(ModelView(User, db.session))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/compressimage', methods=['GET', 'POST'])
def compress_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        img = Image.open(io.BytesIO(file.read()))
        compressed_img = io.BytesIO()
        img.convert("RGB").save(compressed_img, format='JPEG', quality=20)
        compressed_img.seek(0)

        # Save the compressed image to a file (optional)
        compressed_img_filename = 'compressed_image.jpg'
        compressed_img_path = f'static/{compressed_img_filename}'
        with open(compressed_img_path, 'wb') as f:
            f.write(compressed_img.getvalue())

        compressed_img_url = f'/static/{compressed_img_filename}'
        flash("Image compressed successfully!")
        return render_template('compressimage.html', compressed_img_url=compressed_img_url)

    return render_template('compressimage.html')









@app.route('/resizeimage', methods=['GET', 'POST'])
def resize_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        width = int(request.form['width'])
        height = int(request.form['height'])

        img = Image.open(io.BytesIO(file.read()))
        resized_img = img.resize((width, height))  # Resize the image
        resized_img_bytes = io.BytesIO()
        resized_img.save(resized_img_bytes, format='JPEG')
        resized_img_bytes.seek(0)

        # Save the resized image to a file (optional)
        resized_img_filename = 'resized_image.jpg'
        resized_img_path = f'static/{resized_img_filename}'
        with open(resized_img_path, 'wb') as f:
            f.write(resized_img_bytes.getvalue())

        resized_img_url = f'/static/{resized_img_filename}'
        flash("Image resized successfully!")
        return render_template('resizeimage.html', resized_img_url=resized_img_url)

    return render_template('resizeimage.html')






@app.route('/cropimage', methods=['GET', 'POST'])
def crop_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        img = Image.open(io.BytesIO(file.read()))

        # Check if crop parameters are provided
        crop_box = request.form.getlist('cropBox[]')
        if len(crop_box) != 4:
            flash("Please select the area to crop.")
            return redirect(request.url)

        # Convert crop box coordinates to integers
        crop_box = [int(coord) for coord in crop_box]

        # Crop the image
        cropped_img = img.crop(crop_box)

        # Save the cropped image to a BytesIO object
        cropped_img_bytes = io.BytesIO()
        cropped_img.save(cropped_img_bytes, format='JPEG')
        cropped_img_bytes.seek(0)

        # Pass the cropped image to the template for displaying
        return send_file(
            cropped_img_bytes,
            mimetype='image/jpeg',
            attachment_filename='cropped_image.jpg',
            as_attachment=True
        )

    return render_template('cropimage.html')






@app.route('/converttojpg', methods=['GET', 'POST'])
def convert_to_jpg():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        img = Image.open(io.BytesIO(file.read()))

        # Convert image to RGB mode if it has transparency
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        converted_img_bytes = io.BytesIO()
        img.save(converted_img_bytes, format='JPEG')
        converted_img_bytes.seek(0)

        # Save the converted image to a file (optional)
        converted_img_filename = 'converted_image.jpg'
        converted_img_path = f'static/{converted_img_filename}'
        with open(converted_img_path, 'wb') as f:
            f.write(converted_img_bytes.getvalue())

        converted_img_url = f'/static/{converted_img_filename}'
        flash("Image converted to JPG successfully!")
        return render_template('converttojpg.html', converted_img_url=converted_img_url)

    return render_template('converttojpg.html')






@app.route('/photoeditor', methods=['GET', 'POST'])
def photo_editor():
    # Get the drawn elements from the session or initialize an empty list
    drawnElements = session.get('drawnElements', [])

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        rotation_angle = int(request.form.get('rotationAngle', 0))

        img = Image.open(io.BytesIO(file.read()))

        # Rotate the image based on the rotation angle
        img_rotated = img.rotate(rotation_angle, expand=True)

        # Redraw drawn elements on the rotated image
        if drawnElements:
            draw = ImageDraw.Draw(img_rotated)
            for element in drawnElements:
                color = element['color']
                points = element['points']
                for i in range(1, len(points)):
                    draw.line([points[i - 1], points[i]], fill=color, width=5)

        # Save the rotated image to a BytesIO object
        rotated_img_bytes = io.BytesIO()
        img_rotated.save(rotated_img_bytes, format='JPEG')
        rotated_img_bytes.seek(0)

        # Send the rotated image back to the client
        return send_file(
            rotated_img_bytes,
            mimetype='image/jpeg'
        )
    else:
        return render_template('photoeditor.html')
    







@app.route('/upscale', methods=['GET', 'POST'])
def up_scale():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            upscaled_img_path = upscale_image(file_path)
            if upscaled_img_path:
                return render_template('upscale.html', upscaled_img_url=upscaled_img_path)
            else:
                flash("Failed to upscale the image")
                return redirect(request.url)

    return render_template('upscale.html')

def upscale_image(file_path):
    try:
        img = Image.open(file_path)
        
        # Resize the image using Lanczos resampling for better quality
        scaling_factor = 2
        upscaled_img = img.resize((img.width * scaling_factor, img.height * scaling_factor), Image.LANCZOS)
        
        # Save the upscaled image with higher quality
        upscaled_img_filename = secure_filename('upscaled_' + file_path.split('/')[-1])
        upscaled_img_path = os.path.join('static', 'uploads', upscaled_img_filename)
        upscaled_img.save(upscaled_img_path, quality=95)  # Adjust the quality as needed (0 to 100)
        
        return upscaled_img_path
    except Exception as e:
        print(f"Error upscaling image: {e}")
        return None






def remove_background(file_path):
    try:
        img = Image.open(file_path)
        
        # Placeholder for background removal logic
        # Example: Convert image to grayscale and apply thresholding to segment foreground/background
        gray_img = img.convert('L')  # Convert image to grayscale
        threshold = 100  # Adjust the threshold value as needed
        binary_img = gray_img.point(lambda p: p > threshold and 255)  # Apply thresholding
        inverted_binary_img = ImageOps.invert(binary_img)  # Invert the binary image
        cleaned_img = img.copy()  # Create a copy of the original image
        cleaned_img.putalpha(inverted_binary_img)  # Set alpha channel based on the inverted binary image
        
        # Save the processed image
        processed_img_filename = secure_filename('removed_bg_' + file_path.split('/')[-1])
        processed_img_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_img_filename)
        cleaned_img.save(processed_img_path)
        
        return processed_img_path
    except Exception as e:
        print(f"Error removing background from image: {e}")
        return None

@app.route('/removebackground', methods=['GET', 'POST'])
def removebackground():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash("No file selected")
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash("No file selected")
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                processed_img_path = remove_background(file_path)
                if processed_img_path:
                    flash("Background removed successfully!")
                    return render_template('removebackground.html', processed_img_url=processed_img_path)
                else:
                    flash("Failed to remove background from the image")
                    return redirect(request.url)
            else:
                flash("Unsupported file format. Please upload an image file.")
                return redirect(request.url)
        except Exception as e:
            print(f"Error removing background from image: {e}")
            flash("Failed to remove background from the image")
            return redirect(request.url)
    
    return render_template('removebackground.html', processed_img_url=None)




def convert_image(file_path, target_format):
    try:
        img = Image.open(file_path)
        
        # Convert image to the target format
        converted_img = img.convert(target_format)
        
        # Save the converted image
        converted_img_filename = secure_filename(f'converted_image.{target_format}')
        converted_img_path = os.path.join(app.config['UPLOAD_FOLDER'], converted_img_filename)
        converted_img.save(converted_img_path)
        
        return converted_img_path
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

def convert_image(input_path, target_format):
    # Example: Convert the image using Pillow library
    from PIL import Image
    
    output_path = os.path.splitext(input_path)[0] + '.' + target_format
    
    try:
        # Open image
        with Image.open(input_path) as img:
            # Convert format and save
            img.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

@app.route('/convertfromjpg', methods=['GET', 'POST'])
def convert_from_jpg():
    converted_img_url = None
    
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash("No file selected")
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash("No file selected")
                return redirect(request.url)
            
            target_format = request.form.get('format')
            if target_format not in ALLOWED_EXTENSIONS:
                flash("Invalid target format")
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                converted_img_path = convert_image(file_path, target_format)
                if converted_img_path:
                    flash(f"Image converted to {target_format.upper()} successfully!")
                    converted_img_url = url_for('uploaded_file', filename=os.path.basename(converted_img_path))
                else:
                    flash("Failed to convert image")
            else:
                flash("Unsupported file format. Please upload an image file.")
        except Exception as e:
            print(f"Error converting image: {e}")
            flash("Failed to convert image")
    
    return render_template('convertfromjpg.html', converted_img_url=converted_img_url)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.route('/htmltoimage', methods=['GET', 'POST'])
def html_to_image():
    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            flash("Please provide a URL.", 'error')
            return redirect(url_for('html_to_image'))

        try:
            # Convert HTML to image using imgkit
            imgkit.from_url(url, os.path.join(app.config['UPLOAD_FOLDER'], 'converted_image.jpg'))
            flash("HTML converted to image successfully!", 'success')
            return redirect(url_for('view_image'))
        except Exception as e:
            flash(f"Error converting HTML to image: {e}", 'error')
            return redirect(url_for('html_to_image'))

    return render_template('htmltoimage.html')

@app.route('/viewimage')
def view_image():
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_image.jpg')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        flash("Image not found.", 'error')
        return redirect(url_for('html_to_image'))
    


@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        rotation_angle = int(request.form.get('rotationAngle', 0))

        img = Image.open(io.BytesIO(file.read()))

        # Rotate the image based on the rotation angle
        img_rotated = img.rotate(rotation_angle, expand=True)

        # Save the rotated image to a BytesIO object
        rotated_img_bytes = io.BytesIO()
        img_rotated.save(rotated_img_bytes, format='JPEG')
        rotated_img_bytes.seek(0)

        # Send the rotated image back to the client
        return send_file(
            rotated_img_bytes,
            mimetype='image/jpeg'
        )
    else:
        return render_template('rotate.html')
    

def watermark_image(image_path, watermark_path, output_path):
    try:
        # Open the image and the watermark
        image = Image.open(image_path)
        watermark = Image.open(watermark_path)

        # Resize the watermark to fit the image
        width, height = image.size
        watermark.thumbnail((width / 4, height / 4))

        # Calculate the position to place the watermark
        position = (width - watermark.width, height - watermark.height)

        # Add the watermark to the image
        image.paste(watermark, position, watermark)

        # Save the watermarked image
        image.save(output_path)

        return True
    except Exception as e:
        print(f"Error watermarking image: {e}\n{traceback.format_exc()}")
        return False

@app.route('/watermarkimage', methods=['GET', 'POST'])
def watermark_image_page():
    if request.method == 'POST':
        try:
            # Get the uploaded image and watermark from the form
            image_file = request.files['file']
            watermark_file = request.files['watermark']

            # Save the uploaded files to a temporary location
            image_path = 'temp_image.jpg'
            watermark_path = 'temp_watermark.png'
            output_path = 'watermarked_image.jpg'
            image_file.save(image_path)
            watermark_file.save(watermark_path)

            # Watermark the image
            if watermark_image(image_path, watermark_path, output_path):
                return render_template('watermarkimage.html', watermarked_img_url=output_path)
            else:
                return "Failed to watermark the image."
        except Exception as e:
            return f"Error: {e}"
    else:
        # Render the HTML form for uploading images
        return render_template('watermarkimage.html')
    


@app.route('/blurimage', methods=['GET', 'POST'])
def blur_image_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '_' + file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            blurred_image_url = blur_image(file_path)

            return render_template('blurimage.html', blurred_img_url=blurred_image_url)  # Pass blurred image URL

    return render_template('blurimage.html')


def blur_image(image_path):
    image = Image.open(image_path)
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=10))
    blurred_image_filename = 'blurred_' + os.path.basename(image_path)
    blurred_image_path = os.path.join(app.config['UPLOAD_FOLDER'], blurred_image_filename)
    blurred_image.save(blurred_image_path)
    return blurred_image_path  # Return path to blurred image






@app.route('/memegenerator', methods=['GET', 'POST'])
def memegenerator():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '_' + file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the image and create the meme
            img = Image.open(file_path)
            draw = ImageDraw.Draw(img)
            meme_text = request.form['meme_text']
            draw.text((10, 10), meme_text, fill="white")

            # Save the meme image
            meme_filename = 'meme_' + filename
            meme_path = os.path.join(app.config['UPLOAD_FOLDER'], meme_filename)
            img.save(meme_path)

            # Remove the uploaded image
            os.remove(file_path)

            meme_url = url_for('uploaded_file', filename=meme_filename)
            flash("Meme created successfully!")
            return render_template('memegenerator.html', meme_img_url=meme_url)

    return render_template('memegenerator.html', meme_img_url=None)




sample_results = [
    {"title": "Image Compression", "description": "Learn how to compress images effectively.", "link": "/compressimage"},
    {"title": "Image Resizing", "description": "Explore techniques for resizing images without losing quality.", "link": "/resizeimage"},
    {"title": "Image Cropping", "description": "Discover methods for cropping images to focus on specific areas.", "link": "/cropimage"},
    {"title": "Image Conversion", "description": "Convert images between different formats such as JPG, PNG, and GIF.", "link": "/converttojpg"},
    {"title": "Photo Editing", "description": "Learn about various photo editing techniques and tools.", "link": "/photoeditor"},
    {"title": "Meme Generation", "description": "Create hilarious memes using your own images.", "link": "/memegenerator"},
    {"title": "Background Removal", "description": "Remove backgrounds from images to isolate objects.", "link": "/removebackground"},
    {"title": "Image Blurring", "description": "Apply blur effects to images for privacy or artistic purposes.", "link": "/blurimage"},
    {"title": "Watermarking", "description": "Protect your images by adding watermarks.", "link": "/watermarkimage"},
    {"title": "HTML to Image Conversion", "description": "Convert HTML content to image format for sharing or embedding.", "link": "/htmltoimage"},
]


@app.route('/success', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query'].lower()
        # Perform search
        results = []
        for result in sample_results:
            if query in result['title'].lower():
                results.append(result)
        return render_template('results.html', results=results, query=query)
    return render_template('base.html')



    


if __name__ == "__main__":
    app.run(debug=True)