import sys
import os
import torch
import argparse
from flask import Flask, request
from interface import LSTMInterface


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model_path = 'model.pt'
word2idx_path = 'word2idx.json'


wafInterface = LSTMInterface(device, model_path, word2idx_path)
app = Flask(__name__)

@app.route("/",methods=['GET'])
def info():
    return{'name':'LSTM','threshold1':'0.002','threshold2':'0.006'}

@app.route("/waf", methods=['POST'])
def predict():
    payload = request.form['payload']
    res = wafInterface.get_score(payload=payload)
    print(payload, res)
    return {'score': res}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',required=False,default='0.0.0.0',help='host')
    parser.add_argument('--port',required=False,default='80',help='port')
    args = parser.parse_args()
    app.run(debug=False,host=args.host,port=args.port)

