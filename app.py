from flask import Flask, render_template, g, redirect, url_for, request, Response
import sqlite3
import subprocess
import csv
import io

app = Flask(__name__)
DATABASE = 'remates.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # This makes rows behave like dictionaries
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.execute("SELECT * FROM remates ORDER BY fecha_scrape DESC, id DESC")
    remates = cursor.fetchall()
    return render_template('index.html', remates=remates)

@app.route('/scrape')
def scrape():
    subprocess.run(['python3', 'scraper.py'])
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    db = get_db()
    cursor = db.execute("SELECT fuente, descripcion, link, notas, visto, fecha_scrape FROM remates ORDER BY fecha_scrape DESC, id DESC")
    remates = cursor.fetchall()

    si = io.StringIO()
    cw = csv.writer(si)

    # Write header
    cw.writerow([i[0] for i in cursor.description])
    # Write data
    cw.writerows(remates)

    output = si.getvalue()
    response = Response(output, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=remates.csv"
    return response

@app.route('/delete/<int:remate_id>', methods=['POST'])
def delete_remate(remate_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM remates WHERE id = ?", (remate_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/toggle_visto/<int:remate_id>', methods=['POST'])
def toggle_visto(remate_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE remates SET visto = (CASE WHEN visto = 0 THEN 1 ELSE 0 END) WHERE id = ?", (remate_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/update_notes/<int:remate_id>', methods=['POST'])
def update_notes(remate_id):
    notes = request.form['notes']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE remates SET notas = ? WHERE id = ?", (notes, remate_id))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)