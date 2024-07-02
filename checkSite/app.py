from flask import Flask, request, send_file, jsonify, render_template
from PIL import Image
import os
import zipfile
from check import process_image

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'checkSite/PROCESSED_FOLDER'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_images():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'})

    files = request.files.getlist('files')

    if len(files) == 0:
        return jsonify({'error': 'No selected files'})

    processed_files = []
    summed_classes = {'Bad_Welding': 0, 'Crack': 0, 'Excess_Reinforcement': 0, 'Good_Welding': 0, 'Porosity': 0, 'Spatters': 0}
    for file in files:
        if file:
            filename = file.filename
            image = Image.open(file.stream)
            processed_image, dict2 = process_image(image)  # вызываем вашу функцию обработки изображения
            for key in summed_classes.keys():
                summed_classes[key] = summed_classes[key] + dict2[key]
            temp_path = os.path.join(PROCESSED_FOLDER, filename)
            processed_image.save(temp_path, format='JPEG')
            processed_files.append(temp_path)

    zip_filename = os.path.join(PROCESSED_FOLDER, 'processed_images.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        for processed_file in processed_files:
            zf.write(processed_file, os.path.basename(processed_file))

    response_data = {
        'summed_classes': summed_classes,
        'zip_file': zip_filename
    }
    return jsonify(response_data)

@app.route('/download_zip', methods=['GET'])
def download_zip():
    filepath = 'PROCESSED_FOLDER\processed_images.zip'
    return send_file(filepath, mimetype='application/zip', as_attachment=True)

if __name__ == '__main__':
    app.run()
