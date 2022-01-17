from flask import Flask, jsonify, request
import sqlite3
import pandas as pd
import os
import datetime
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>API TWITTER</h1><p>This site is a prototype API for sentimental prediction of tweets.</p>"

@app.route('/api/v1/create_db', methods=['GET'])
def createdb():
    con = sqlite3.connect("tweets_ver_polarity.db")
    cursor = con.cursor()
    cursor.execute("DROP TABLE IF EXISTS t;")
    cursor.execute("CREATE TABLE t (polarity, text, created_at, retweet_count, username, followers_count, verified);")
    df = pd.read_csv("tweets_ver_polarity.csv")
    for row in df.itertuples():
        cursor.execute('''
                    INSERT INTO t (polarity, text, created_at, retweet_count, username, followers_count, verified)
                    VALUES ('%s','%s','%s','%s','%s','%s','%s')
                    ''' % (row.polarity, row.text, row.created_at, row.retweet_count, row.username, row.followers_count, row.verified)
                     )
    con.commit()
    results = cursor.execute("SELECT * FROM t ;").fetchall()
    con.close()
    return jsonify(results)

# @app.route('/api/v1/new_register', methods=['POST'])
# def new_register():
#     con = sqlite3.connect('tweets.db')
#     cursor = con.cursor()

#     text = request.args.get('text', None)
#     created_at = request.args.get('created_at', None)
#     retweet_count = request.args.get('retweet_count', None)
#     username = request.args.get('username', None)
#     followers_count = request.args.get('followers_count', None)
#     verified = request.args.get('verified', None)
#     polarity = request.args.get('polarity', None)
#     list_values = [text, created_at, retweet_count, username, followers_count, verified, polarity]

#     if text is None or created_at is None or retweet_count is None or username is None or followers_count is None or verified is None or polarity is None:
#         return "Args empty, the data were not stored"
#     else:
#         cursor.execute('INSERT INTO t (text, created_at, retweet_count, username, followers_count, verified, polarity) VALUES (?, ?, ? , ?, ?, ?, ?);',list_values)
    
#     con.commit()
#     results = cursor.execute("SELECT * FROM t ORDER BY 1 ASC ;").fetchall()
#     con.close()
    
#     return jsonify(results)


@app.route('/api/v1/predict', methods=['GET'])
def predict():
    
    text = request.args.get("text", None)

    if text is None:
        return "Args empty, the data are not enough to predict"
    else:
        with open("tweets.model", 'rb') as archivo_entrada:
            model = pickle.load(archivo_entrada)
        prediction = model.predict([text])
    
    return jsonify({"predictions": prediction[0]})

@app.route('/api/v1/retrain', methods=['PUT'])
def retrain():
    con = sqlite3.connect("tweets_ver_polarity.db")
    cursor = con.cursor()
    data = cursor.execute('SELECT * FROM t').fetchall()
    con.close()

    data = pd.DataFqrame(data, columns= ["text"])

    X_train, X_test, y_train, y_test = train_test_split(data.drop(columns=["text"]),
                                                        data["text"],
                                                        test_size = 0.20,
                                                        random_state=42)

    lin_reg = LinearRegression()
    lin_reg.fit(X_train, y_train)

    pickle.dump(lin_reg, open("tweets.model", 'wb'))

    return "Finished train succesfully"

app.run()