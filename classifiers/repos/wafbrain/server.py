import argparse
from flask import Flask,request
from interface import WafBrainInterface

# import tensorflow as tf
# os.environ["CUDA_VISIBLE_DEVICES"] = "cuda:0"
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# config = tf.compat.v1.ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.5
# tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session(config=config))

wafBrainInterface = WafBrainInterface()
app = Flask(__name__)

@app.route("/",methods=['GET'])
def info():
    return{'name':'CNN','threshold1':'0.100','threshold2':'0.333','threshold3':'0.500'}

@app.route("/waf", methods=['POST'])
def predict():
    payload=request.form['payload']
    res = wafBrainInterface.get_score(payload=payload)
    print(payload,res)
    return {'score':res}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',required=False,default='0.0.0.0',help='host')
    parser.add_argument('--port',required=False,default='80',help='port')
    args = parser.parse_args()
    app.run(debug=False,host=args.host,port=args.port)
