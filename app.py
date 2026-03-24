import os
import numpy as np
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import easyocr
import cv2
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR
print("Loading EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR loaded successfully!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get image info
            img = cv2.imread(filepath)
            height, width = img.shape[:2]
            file_size = os.path.getsize(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'width': width,
                'height': height,
                'file_size': round(file_size / 1024, 2)
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image = cv2.imread(filepath)
            
            # Extract text
            results = reader.readtext(image)
            
            # Process results
            words = []
            full_text = ""
            
            for (bbox, text, confidence) in results:
                words.append({
                    'text': text,
                    'confidence': round(float(confidence) * 100, 2)
                })
                full_text += text + " "
            
            return jsonify({
                'success': True,
                'text': full_text.strip(),
                'words': words,
                'count': len(words)
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("OCR Text Recognition App")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)