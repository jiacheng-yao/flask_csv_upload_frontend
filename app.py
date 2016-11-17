from flask import Flask, render_template, json, request,redirect,session,jsonify
from flask.ext import excel

import pandas as pd

from werkzeug import generate_password_hash, check_password_hash

from sqlalchemy_declarative import CSVUpload_User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json
import requests

import settings

app = Flask(__name__)
app.secret_key = settings.CSVUPLOAD_APP_SECRET_KEY

@app.route('/')
def main():
    if session.get('user'):
        return render_template('uploadCSV.html')
    else:
        return render_template('signin.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('uploadCSV.html')
    else:
        return render_template('signin.html')

@app.route('/uploadCSV')
def showUploadCSV():
    if session.get('user'):
        return render_template('uploadCSV.html')
    else:
        return render_template('error.html', error='Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/reports')
def showReports():
    try:
        if session.get('user'):
            result = requests.get('http://{}:{}/bidmod/report_list/{}'.format(settings.BIDMOD_SERVER_HOST,
                                                                              settings.BIDMOD_SERVER_PORT,
                                                                              session['user']))

            result_json = result.json()

            result_df = pd.DataFrame(result_json['data'])

            if not result_df.empty:
                result_df.drop(['task_id', 'username', 'comment'], axis=1, inplace=True)

                result_df = result_df.rename(columns={'filename': 'title'})

                result_df['started_at'] = [str(tmp).split('.')[0] for tmp in pd.to_datetime(result_df['started_at'])]
                result_df['created_at'] = [str(tmp).split('.')[0] for tmp in pd.to_datetime(result_df['created_at'])]
                result_df['finished_at'] = [str(tmp).split('.')[0] for tmp in pd.to_datetime(result_df['finished_at'])]

                result_df['download_link'] = result_df['id'].apply(lambda x:
                                                                   '<a href="http://{}:{}/bidmod/{}/download">Download</a>'.
                                                                   format(settings.BIDMOD_FILE_DOWNLOAD_HOST,
                                                                          settings.BIDMOD_FILE_DOWNLOAD_PORT,
                                                                          x))

                result_df.set_index(['id'], inplace=True)
                result_df.index.name = 'Task'

                result_df = result_df[['venture', 'status', 'validate_only',
                                       'title', 'error_message', 'created_at',
                                       'started_at', 'finished_at', 'download_link']]

                pd.set_option('display.max_colwidth', 1000)

                return render_template('reports.html',
                                       df=result_df.to_html(escape=False))
            else:
                return render_template('reports_empty.html')

    except Exception as e:
        return render_template('error.html', error = str(e))


@app.route('/do_uploadCSV',methods=['POST'])
def UploadCSV():
    try:
        if session.get('user'):

            username = session['user']
            filename = request.form['filename']
            venture = request.form['venture']

            f = request.files['file']
            csv_data = f.stream.read()

            if isinstance(csv_data, str):
                csv_data = csv_data.decode('ISO-8859-1')

            validate_only = 'validate_only' in request.form
            comment = request.form['comment']

            result = requests.post('http://{}:{}/bidmod/upload'.format(settings.BIDMOD_SERVER_HOST,
                                                                      settings.BIDMOD_SERVER_PORT),
                                   data={"username": username,
                                         "filename": filename,
                                         "venture": venture,
                                         "csv_data": json.dumps(csv_data),
                                         "validate_only": validate_only,
                                         "comment": comment})

            return render_template('uploadCSV.html')
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputUsername']
        _password = request.form['inputPassword']

        engine = create_engine('sqlite:///csvupload_user.db')
        Base.metadata.bind = engine

        DBSession = sessionmaker()
        DBSession.bind = engine
        db_session = DBSession()

        user = db_session.query(CSVUpload_User).filter(CSVUpload_User.username == _username).one()

        if check_password_hash(user.password,_password):
            session['user'] = user.id
            return redirect('/uploadCSV')
        else:
            return render_template('error.html',error = 'Wrong Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
