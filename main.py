import datetime

from flask import Flask, render_template, flash, request, session
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, TextAreaField, FileField
from wtforms.validators import DataRequired, ValidationError, Length
import mysql.connector
import time
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'Qwerty123!'


# połączenie z baza MySQL
mysqlDB = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    database='zadania'
)

# tworzenie kursora do bazy danych
mysqlCursor = mysqlDB.cursor()

mysqlCursor.execute("""CREATE TABLE IF NOT EXISTS zadania2 (
    zadanie VARCHAR(255),
    data VARCHAR(255),
    godzina VARCHAR(255),
    wykonane VARCHAR(3),
    ID INT AUTO_INCREMENT PRIMARY KEY)""")


class zadanieFormDefault(FlaskForm):
    """Formularz wprowadzania danych"""
    zadanie = StringField('Zadanie', validators=[DataRequired()])
    Data = StringField('Data wykonania (dd.mm.yyyy)', validators=[DataRequired()])
    godzina = StringField('Godzina wykonania (hh:mm)', validators=[DataRequired()])
    submit = SubmitField('Zapisz dane')

@app.route('/')
def index():
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania',
    )
    dbCursor = dbConnection.cursor()
    dbCursor.execute('SELECT * FROM zadania2 ORDER BY ID ')
    lastAddedRecords = dbCursor.fetchall()
    j = 0
    tab = []

    # czas
    now = datetime.now()

    for record in lastAddedRecords:
        tab2 = []
        for r in record:
            tab2.append(r)
        tab.append(tab2)
        j+=1

    i = 0

    for t in tab:
        r = t[1] + " " + t[2]
        deadline = datetime.strptime(r, "%d.%m.%Y %H:%M")
        ileDoKonca = deadline - now

        if t[3] == "Tak":
            tab[i].append(False)
            tab[i].append(True)
            tab[i].append(False)
            tab[i].append(True)
        else:
            tab[i].append(True)
            tab[i].append(False)
            if ileDoKonca > timedelta(0):
                tab[i].append(False)
                tab[i].append(True)
            else:
                tab[i].append(True)
                tab[i].append(False)
        i+=1
        if i == j:
            break
    color = "green"

    return render_template('index.html', title='Strona główna', lastAddedRecords=tab, color=color)

# funkcja renderująca formularz
@app.route('/zadanieForm')
def zadanieForm():
    zadanieForm = zadanieFormDefault()
    if zadanieForm.validate_on_submit():
        zadanie = zadanieForm.zadanie.data = ''
        Data = zadanieForm.Data.data = ''
        godzina = zadanieForm.godzina.data = ''
    return render_template('zadanieForm.html', title='Dodaj kontakt - formularz', zadanieForm=zadanieForm)


@app.route('/addZadanie', methods=['POST'])
def addContact():
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania'
    )
    dbCursor = dbConnection.cursor()
    zadanie = request.form['zadanie']
    Data = request.form['Data']
    godzina = request.form['godzina']
    sql = "INSERT INTO zadania2 (zadanie, data, godzina, wykonane) VALUES (%s, %s, %s, 'Nie')"
    values = (zadanie, Data, godzina)
    dbCursor.execute(sql, values)

    # dodanie danych do bazy
    dbConnection.commit()

    flash('Dane zapisane poprawnie!')

    dbCursor.execute('SELECT * FROM zadania2 ORDER BY ID DESC LIMIT 1')
    lastAddedRecords = dbCursor.fetchall()


    return render_template('addZadanie.html', title='Dodaj zadanie - zapisano', lastAddedRecords=lastAddedRecords)

@app.route('/editZadanie')
def editContact():
    ID = request.args.get('ID')
    session['ID'] = ID
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania'
    )
    dbCursor = dbConnection.cursor()
    dbCursor.execute('SELECT * FROM zadania2 WHERE ID = ' + ID)
    records = dbCursor.fetchall()
    for record in records:
        editZadanieForm = zadanieFormDefault(zadanie=record[0], Data=record[1], godzina=record[2])
    return render_template('editZadanie.html', title='Edycja kontaktu', editZadanieForm=editZadanieForm)

@app.route('/saveZadanie', methods=['POST'])
def saveContact():
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania'
    )
    ID = session['ID']
    dbCursor = dbConnection.cursor()
    zadanie = request.form['zadanie']
    Data = request.form['Data']
    godzina = request.form['godzina']
    sql = "UPDATE zadania2 SET zadanie = %s, Data = %s, godzina = %s WHERE ID = " + ID
    values = (zadanie, Data, godzina)
    dbCursor.execute(sql, values)
    dbConnection.commit()
    dbCursor.execute('SELECT * FROM zadania2 WHERE ID = ' + ID)
    editRecord = dbCursor.fetchall()
    return render_template('saveZadanie.html', title='Zadanie zapisany', editRecord=editRecord)

@app.route('/deleteZadanie')
def deleteContact():
    ID = request.args.get('ID')
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania'
    )
    dbCursor = dbConnection.cursor()
    dbCursor.execute('DELETE FROM zadania2 WHERE ID = ' + ID)
    dbConnection.commit()
    dbCursor.execute('SELECT * FROM zadania2 ORDER BY ID')
    records = dbCursor.fetchall()
    return render_template('deleteZadanie.html', title='Zadanie usunięty', records=records)

@app.route('/change')
def change():
    ID = request.args.get('ID')
    dbConnection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        database='zadania',
    )
    dbCursor = dbConnection.cursor()
    sql = "UPDATE zadania2 SET wykonane = 'Tak' WHERE ID = " + ID
    dbCursor.execute(sql)
    dbConnection.commit()
    dbCursor.execute('SELECT * FROM zadania2 ORDER BY ID ')
    lastAddedRecords = dbCursor.fetchall()
    j = 0
    tab = []

    for record in lastAddedRecords:
        tab2 = []
        for r in record:
            tab2.append(r)
        tab.append(tab2)
        j += 1
    now = datetime.now()
    i = 0
    for t in tab:
        r = t[1] + " " + t[2]
        deadline = datetime.strptime(r, "%d.%m.%Y %H:%M")
        ileDoKonca = deadline - now

        if t[3] == "Tak":
            tab[i].append(False)
            tab[i].append(True)
            tab[i].append(False)
            tab[i].append(True)
        else:
            tab[i].append(True)
            tab[i].append(False)
            if ileDoKonca > timedelta(0):
                tab[i].append(False)
                tab[i].append(True)
            else:
                tab[i].append(True)
                tab[i].append(False)
        i += 1
        if i == j:
            break
    color = "green"
    return render_template('index.html', title='Strona główna', lastAddedRecords=tab, color=color)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html', title='404'), 404

@app.errorhandler(500)
def internalServerError(error):
    return render_template('500.html', title='500'), 500

if __name__ == '__main__':
    app.run(debug=True)