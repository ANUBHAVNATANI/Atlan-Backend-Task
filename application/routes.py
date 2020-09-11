import os
from flask import Flask, request, redirect, jsonify,render_template,current_app as app
from werkzeug.utils import secure_filename
import threading
from . import db
import traceback
import json
from .models import Form,Team
import pandas as pd
from sqlalchemy import and_, func
from datetime import date
#setting the current status
STATUSES = app.config['STATUSES']
STATUS = STATUSES[0]

#thread event
th_event = threading.Event()

#helper functions
def is_stopped():
    global STATUS
    return 1 if STATUS == STATUSES[3] else 0

def is_paused():
    global STATUS
    return 1 if STATUS == STATUSES[2] else 0

def is_uploading():
    global STATUS
    return 1 if STATUS == STATUSES[1] else 0

def is_uploaded():
    global STATUS
    return 1 if STATUS == STATUSES[4] else 0

def is_exporting():
    global STATUS
    return 1 if STATUS == STATUSES[5] else 0

def get_date(date_range_1,date_range_2):
    date_range_1 = list(map(int,date_range_1.split('/')))
    date_range_2 = list(map(int,date_range_2.split('/')))
    date_range_1 = date(day=date_range_1[1],month=date_range_1[0],year=date_range_1[2])
    date_range_2 = date(day=date_range_2[1],month=date_range_2[0],year=date_range_2[2])
    return [date_range_1,date_range_2]


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/createTeams',methods=['POST'])
def create_teams():
    if request.method == "POST":
        global STATUS
        if STATUS == STATUSES[1]:
            resp = jsonify({'message': 'Wait for upload to complete'})
            resp.status_code = 400
            return resp
        if 'file' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        file_ext = os.path.splitext(filename)[1]
        if uploaded_file and file_ext in app.config['ALLOWED_EXTENSIONS']:
            filestream = uploaded_file.stream
            #setting the internal flag of the therad to true
            th_event.set()
            flag = 1
            STATUS = STATUSES[1]
            print("Adding teams to the database")
            count = 0
            db.session.begin_nested()
            for line in filestream:
                th_event.wait()
                if STATUS == STATUSES[3]:
                    flag = 0
                    break
                if count>0:
                    line = line.decode('UTF-8')
                    print(line)
                    team = line.split(",")
                    new_team = Team(t_id = team[0],name=team[1],number=team[2])
                    db.session.add(new_team)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        resp = jsonify({'message':e})
                        resp.status_code = 400
                        break
                        return resp
                count+=1
            if flag == 0:
                db.session.rollback()
                db.session.close()
                resp = jsonify({'message': 'Teams creation stopped'})
                resp.status_code = 201
                return resp
            db.session.close()
            STATUS = STATUSES[0]
            print("Teams Added")
            resp = jsonify({'message': 'Teams Added'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message': 'Please upload .csv file'})
            resp.status_code = 400
            return resp

@app.route('/getTeams',methods=['GET'])
def get_teams():
    try:
        #retrive each team from the database 
        teams_list = Team.query.all()
        teams = {}
        for team in teams_list:
            try:
                teams[team.t_id] = (team.name,team.number)
            except:
                resp = jsonify({'message':"error"})
                resp.status_code = 400
                return resp
        res = jsonify(teams)
        res.status_code = 201
        return res
    except:
        return jsonify({'trace':traceback.format_exc()})

@app.route('/export',methods=['GET','POST'])
def export_data():
    try:
        date_range = get_date(request.form['date_range_1'],request.form['date_range_2'])
        qry = db.session.query(Form).filter(and_(Form.date <= date_range[1], Form.date >= date_range[0])).all()
        quries = {}
        th_event.set()
        flag = 1
        STATUS = STATUSES[5]
        for form in qry:
            th_event.wait()
            if STATUS == STATUSES[3]:
                flag = 0
                break
            quries[form.f_id] = {'name':form.name,'date':form.date,'gender':form.gender}
        if flag == 0:
            return jsonify({'message': "Export was stopped"})
        else:
            return jsonify(quries)
    except Exception as e:
        resp = jsonify({'message': e})
        resp.status_code = 400
        return resp


@app.route('/baselineUpload', methods=['POST'])
def upload_file():
    if request.method == "POST":
        global STATUS
        if STATUS == STATUSES[1]:
            resp = jsonify({'message': 'Wait for upload to complete'})
            resp.status_code = 400
            return resp
        if 'file' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        file_ext = os.path.splitext(filename)[1]
        if uploaded_file and file_ext in app.config['ALLOWED_EXTENSIONS']:
            filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
            filestream = uploaded_file.stream
            #setting the internal flag of the therad to true
            th_event.set()
            flag = 1
            STATUS = STATUSES[1]
            print("Uplaoding file...")
            print(filepath)
            if not os.path.exists(app.config['UPLOAD_PATH']):
                os.makedirs(app.config['UPLOAD_PATH'])
            with open(filepath, 'wb') as newfile:
                for line in filestream:
                    th_event.wait()
                    if STATUS == STATUSES[3]:
                        flag = 0
                        break
                    print(line, sep='')
                    newfile.write(line)
            if flag == 0:
                STATUS = STATUSES[3]
                os.remove(filepath)
                print("File upload was stopped")
                resp = jsonify({'message': 'File upload was stopped'})
                resp.status_code = 201
                return resp
            STATUS = STATUSES[0]
            print("File uploaded")
            #store the file data in database
            try:
                forms_data = pd.read_csv(filepath)
                forms_data['date'] = pd.to_datetime(forms_data['date'],format= "%m/%d/%Y")
                forms_data.to_sql(name="forms_data",con=db.engine,index=False,if_exists="append")
            except Exception as e:
                db.session.rollback()
                resp = jsonify({'message':e})
                resp.status_code = 400
                return resp
            finally:
                db.session.close()
                os.remove(filepath)
            resp = jsonify({'message': 'Records added to database using baseline upload'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message': 'Please upload .csv file'})
            resp.status_code = 400
            return resp

@app.route('/status', methods=['GET', 'POST', 'PUT'])
def get_status():
    global STATUS
    resp = jsonify({'status': STATUS})
    resp.status_code = 201
    return resp

@app.route('/pause', methods=['GET', 'POST', 'PUT'])
def pause_upload():
    global STATUS
    if STATUS != STATUSES[1]:
        print('Pause not required', STATUS)
        resp = jsonify({'message': 'Pause not required'})
        resp.status_code = 201
        return resp
    th_event.clear()
    STATUS = STATUSES[2]
    print(STATUS)
    resp = jsonify({'message': 'Task paused'})
    resp.status_code = 201
    return resp

@app.route('/resume', methods=['GET', 'POST', 'PUT'])
def resume_upload():
    global STATUS
    if STATUS != STATUSES[2]:
        print('Not required', STATUS)
        resp = jsonify({'message': 'Resume not required'})
        resp.status_code = 201
        return resp
    th_event.set()
    STATUS = STATUSES[1]
    print(STATUS)
    resp = jsonify({'message': 'Task resumed'})
    resp.status_code = 201
    return resp

@app.route('/stop', methods=['GET', 'POST', 'PUT'])
def stop_upload():
    global STATUS
    if STATUS != STATUSES[1] and STATUS != STATUSES[2]:
        print('Stop not required', STATUS)
        resp = jsonify({'message': 'Already Stopped'})
        resp.status_code = 201
        return resp
    th_event.set()
    STATUS = STATUSES[3]
    print('Stopping')
    resp = jsonify({'message':'Stopping'})
    resp.status_code = 201
    return resp

@app.route('/clearDatabase',methods=['GET', 'POST', 'PUT'])
def clear_database():
    try:
        Form.query.delete()
        Team.query.delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({"message":"Deleted data from both tables"})
