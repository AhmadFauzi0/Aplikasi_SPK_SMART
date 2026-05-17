from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import numpy as np
import io
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import base64

from core.models import init_db, Project, SessionLocal
from core.engine import SMARTEngine, SMARTInput

app = Flask(__name__)
app.secret_key = "smart_unpam_secret"
init_db()
engine = SMARTEngine()

@app.route('/')
def index():
    with SessionLocal() as db:
        projects = db.query(Project).all()
    return render_template('index.html', projects=projects)

@app.route('/materi')
def view_materi():
    return render_template('materi.html')

@app.route('/project/create', methods=['POST'])
def create_project():
    name = request.form.get('name')
    desc = request.form.get('description')
    default_data = {
        "criteria": ["Biaya", "Kualitas", "Fleksibilitas"],
        "types": ["cost", "benefit", "benefit"],
        "weights": [40.0, 40.0, 20.0],
        "weight_method": "direct",
        "alternatives": ["Vendor A", "Vendor B"],
        "performance": [[150, 80, 70], [120, 75, 85]]
    }
    with SessionLocal() as db:
        if db.query(Project).filter(Project.name == name).first():
            flash("Nama proyek sudah digunakan!", "danger")
        else:
            new_p = Project(name=name, description=desc, data_json=default_data)
            db.add(new_p)
            db.commit()
    return redirect(url_for('index'))

@app.route('/project/<int:id>')
def view_project(id):
    with SessionLocal() as db:
        project = db.query(Project).get(id)
    if not project: return "Proyek tidak ditemukan", 404
    return render_template('project.html', project=project, data=project.data_json)

@app.route('/project/<int:id>/update', methods=['POST'])
def update_data(id):
    criteria = request.form.getlist('criteria[]')
    types = request.form.getlist('types[]')
    weights = [float(w) for w in request.form.getlist('weights[]')]
    alternatives = request.form.getlist('alternatives[]')
    weight_method = request.form.get('weight_method', 'direct')
    
    perf_flat = [float(p) for p in request.form.getlist('perf[]')]
    performance = np.array(perf_flat).reshape(len(alternatives), len(criteria)).tolist()
    
    updated_json = {
        "criteria": criteria, "types": types, "weights": weights,
        "weight_method": weight_method,
        "alternatives": alternatives, "performance": performance
    }
    
    with SessionLocal() as db:
        proj = db.query(Project).get(id)
        proj.data_json = updated_json
        db.commit()
        
    flash("Data Proyek Berhasil Diperbarui!", "success")
    return redirect(url_for('view_project', id=id))

@app.route('/project/<int:id>/upload', methods=['POST'])
def upload_file(id):
    file = request.files.get('file')
    if not file:
        flash("File tidak ditemukan", "danger")
        return redirect(url_for('view_project', id=id))
        
    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
    alts = df.iloc[:, 0].astype(str).tolist()
    criteria = df.columns[1:].tolist()
    performance = df.iloc[:, 1:].values.astype(float).tolist()
    
    with SessionLocal() as db:
        proj = db.query(Project).get(id)
        current_data = proj.data_json
        current_data["criteria"] = criteria
        current_data["types"] = ["benefit"] * len(criteria)
        current_data["weights"] = [100.0 / len(criteria)] * len(criteria)
        current_data["weight_method"] = "direct"
        current_data["alternatives"] = alts
        current_data["performance"] = performance
        proj.data_json = current_data
        db.commit()
        
    flash("Data Berhasil Diunggah!", "success")
    return redirect(url_for('view_project', id=id))

@app.route('/project/<int:id>/calculate')
def calculate_project(id):
    with SessionLocal() as db:
        proj = db.query(Project).get(id)
    p_data = proj.data_json
    
    inp = SMARTInput(
        alternatives=p_data['alternatives'], criteria=p_data['criteria'],
        performance=np.array(p_data['performance']), weights_raw=np.array(p_data['weights']),
        types=p_data['types'], weight_method=p_data.get('weight_method', 'direct')
    )
    
    results = engine.calculate(inp)
    
    target_idx = 0 
    w_vals, scores_history = engine.run_oat_sensitivity(inp, target_idx)
    
    plt.figure(figsize=(8, 4))
    for i, name in enumerate(p_data['alternatives']):
        alt_scores = [step[i] for step in scores_history]
        plt.plot(w_vals, alt_scores, marker='o', linestyle='-', label=name)
    plt.xlabel(f"Perubahan Bobot Kriteria: {p_data['criteria'][target_idx]}")
    plt.ylabel("Skor Akhir SMART V(a_i)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    img_buf.seek(0)
    plt.close()
    
    chart_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    return render_template('results.html', project=proj, data=p_data, res=results, chart=chart_base64)

@app.route('/project/<int:id>/export')
def export_excel(id):
    with SessionLocal() as db:
        proj = db.query(Project).get(id)
    p_data = proj.data_json
    df = pd.DataFrame(p_data['performance'], columns=p_data['criteria'], index=p_data['alternatives'])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Matriks')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"Data_SMART_{proj.name}.xlsx")

@app.route('/project/<int:id>/delete')
def delete_project(id):
    with SessionLocal() as db:
        proj = db.query(Project).get(id)
        if proj:
            db.delete(proj)
            db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)