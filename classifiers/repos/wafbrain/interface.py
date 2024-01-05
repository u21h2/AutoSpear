import os
import hashlib
from tensorflow.keras.models import load_model
from waf_brain.inferring import process_payload

class WafBrainInterface():
    def __init__(self, score_threshold=0.1):
        model_path = os.path.join(os.path.dirname(__file__), 'waf-brain.h5')
        self.model = load_model(model_path)
        self.score_threshold = score_threshold
        self.process_count = 1
        self.dict = {}

    def get_score(self, payload):
        if self.process_count > 10000:
            self.process_count = 0
            del self.dict
            self.dict = {}
        self.process_count += 1
        hashkey = hashlib.md5(payload.encode('utf-8')).hexdigest()
        if hashkey in self.dict:
            return self.dict[hashkey]
        else:
            result = process_payload(self.model, 'q', [payload], False)
            if result is None:
                result = {'score': 1.0}
            score = result['score']
            self.dict[hashkey] = score
            return score
