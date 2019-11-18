import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
import datetime 

app = Flask(__name__)


# Mining a Block
@app.route('/user_login', methods=['GET'])
def user_login():
    json = request.get_json() 
    login_keys = ['username','password'] 
    if not all(key in json for key in login_keys):
        return 'Some elements of the login are missing.',400 
    if json['username']=='5001':
        if json['password']=='5001':
            data = {"nodes": ["http://127.0.0.1:5002","http://127.0.0.1:5003"]}
            response = requests.post('http://127.0.0.1:5001/connect_node',data)  
            if response.status_code == '201':
                response = {'message': 'All set Mr.5001 the nodes are now connected.'}
                return jsonify(response),201 
        else:
            response = {'message':'It looks like you have entered wrong password.Please try again.....'}
    elif json['username']=='5002':
        if json['password']=='5002':
            data = {"nodes": ["http://127.0.0.1:5001","http://127.0.0.1:5003"]}
            response = requests.post('http://127.0.0.1:5002/connect_node',data)  
            if response.status_code == '201':
                response = {'message': 'All set Mr.5002 the nodes are now connected.'}
                return jsonify(response),201 
        else:
            response = {'message':'It looks like you have entered wrong password.Please try again.....'}
    elif json['username']=='5003':
        if json['password']=='5003':
            data = {"nodes": ["http://127.0.0.1:5001","http://127.0.0.1:5003"]}
            response = requests.post('http://127.0.0.1:5003/connect_node',data)  
            if response.status_code == '201':
                response = {'message': 'All set Mr.5003 the nodes are now connected.'}
                return jsonify(response),201 
        else:
            response = {'message':'It looks like you have entered wrong password.Please try again.....'}
    else:
        response = {'message':'It looks like you have entered wrong username.Please try again.....'}
        return jsonify(response),401
    return 401



app.run(host='0.0.0.0', port=2001)

