import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from converter import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Upload dizinini oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Koordinat dönüşümü için projeksiyonları tanımla
proj_dict = {
    'ED50': {
        'zones': ['Zone 1', 'Zone 2', 'Zone 3']  # ED50 için örnek zonlar
    },
    'ITRF96': {},
    'WGS84': {}
}

@app.route('/')
def upload_form():
    return render_template('index.html', proj_dict=proj_dict)

@app.route('/epsg')
def read_epsg_codes():
    return render_template('epsg.json')

@app.route('/upload', methods=['POST'])
def upload_file():
    source_coord_type = request.form['source_coord_type']  # Koordinat türünü al
    target_coord_type = request.form['target_coord_type'] 
    print(source_coord_type, target_coord_type)
    if "file" not in request.files:
        flash('Dosya seçilmedi!')
        return jsonify({'error': 'Dosya bulunamadı'}), 400
    
    file = request.files["file"]
    if file.filename == '':
        flash('Dosya adı boş!')
        return redirect(request.url)
    source_coord_type = request.form['source_coord_type']  # Koordinat türünü al
    target_coord_type = request.form['target_coord_type']  # Koordinat türünü al
    source_epsg_code = get_epsg_code(source_coord_type)
    target_epsg_code = get_epsg_code(target_coord_type)

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        coordinates = []
        output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_coordinates.txt')  # Dönüştürülmüş koordinatlar dosyası

        with open(file_path, 'r') as f:
            with open(output_file_path, 'w') as output_file:
                for line in f:
                    x, y = map(float, line.strip().split(','))

                    lat, lon = convert_coordinate(x, y, source_epsg_code, target_epsg_code)    
                        
                    # Koordinatları dosyaya yaz
                    output_file.write(f"{lat},{lon}\n")
                    coordinates.append({'lat': lat, 'lon': lon})

        # Dönüştürülmüş koordinatlar için .txt dosyasını kullanıcıya sun
        return render_template('map.html', coordinates=coordinates, download_link=url_for('download_file', filename='converted_coordinates.txt'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
