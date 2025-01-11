from flask import Flask, request, jsonify, render_template
import cv2
import easyocr
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Allowed file extensions for the image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Path to save uploaded images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

@app.route('/')
def index():
    return render_template('do-an.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    print('aalas')
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the uploaded image with OpenCV and EasyOCR
        img = cv2.imread(file_path)
        results = reader.readtext(img)
        
        license_plate = "None detected"
        for (bbox, text, prob) in results:
            if prob > 0.5:  # Check if the detection confidence is high
                license_plate = text

        return jsonify({
            'success': True,
            'license_plate': license_plate,
            'image_url': file_path
        })
    return jsonify({'success': False, 'message': 'File not allowed'})


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
