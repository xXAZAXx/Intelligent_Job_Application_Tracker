from flask import Flask, render_template, url_for, request, redirect
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def my_SQL_connection():
    connection = sqlite3.connect(r'G:\Projects_Folder\Intelligent Job Application Tracker\instance\test.db')
    return connection

connection = my_SQL_connection()
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS job 
               (id integer PRIMARY KEY AUTOINCREMENT, company text, job_title text, location text, platform text, status text, link text, created text, notes text)''')
connection.commit()
connection.close()

print("BS4 works")
print(requests.__version__)
print("Starting Flask app...")


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new-posting', methods=['POST'])
def new_posting():
    url = request.form.get('url')
    
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    if soup.title:
        page_title = soup.title.string
    else:
        return "Error - No title found", 400
    
    created_at = datetime.now().isoformat()
    job_title = page_title.split(" hiring ")[-1].split(" in ")[0]
    location = page_title.split(" in ")[-1].split(" | ")[0]
    company = page_title.split(" hiring ")[0]
    platform = page_title.split(" | ")[-1]
    status = "Applied"
    notes = ""

    connection = my_SQL_connection()
    cursor = connection.cursor()           
    cursor.execute('''INSERT INTO job (company, job_title, location, platform, status, link, created, notes) VALUES (?,?,?,?,?,?,?,?)''', (company, job_title, location, platform, status,url,created_at, notes))
    connection.commit()
    cursor.execute("SELECT * FROM job")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    connection.close()
    
    return redirect('/table')
   

#"Credo hiring Optical System Test Specialist in 
# Ottawa, Ontario, Canada | LinkedIn"


@app.route('/table', methods=['GET'])
def table():
    connection = my_SQL_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT id, company, job_title, location, platform, created, link, status, notes FROM job")
    rows = cursor.fetchall()
    jobs = [dict(row) for row in rows]
    connection.close()
    return render_template('table.html', jobs=jobs)

@app.route('/edit/<int:job_id>', methods=['GET'])
def edit_job(job_id):
    connection = my_SQL_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM job WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    connection.close()

    if not row:
        return "Job not found", 404

    job = dict(row)
    return render_template('update.html', job=job)

@app.route('/edit/<int:job_id>', methods=['POST'])
def update_job(job_id):
    status = request.form.get('status')
    notes = request.form.get('notes')

    connection = my_SQL_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE job
        SET status = ?, notes = ?
        WHERE id = ?
        """,
        (status, notes, job_id)
    )

    connection.commit()
    connection.close()

    return redirect('/table')

@app.route('/delete-job', methods=['POST'])
def delete_job():
    job_id = request.form.get('job_id')

    connection = my_SQL_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM job WHERE id = ?", (job_id,))

    connection.commit()
    connection.close()

    return redirect('/table')

connection = my_SQL_connection()
cursor = connection.cursor()


if __name__ == "__main__":
    app.run(debug=True)
    