import os
from flask import Flask, flash, request, render_template, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import util

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/drives/windows/htv4app/uploads'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/api/image', methods=["POST"])
def upload_image():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return jsonify(data='')
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return jsonify(data='')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        data_out = util.read_face_gcv(image_path)
        return render_template('results.html', image=filename)
        # return jsonify(data=data_out)

@app.route('/api/text', methods=["POST"])
def upload_text():
    data_out = util.read_text_gcv(request.form['text'])
    return render_template('results.html')
    # return jsonify(data=data_out)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.run(debug=True)