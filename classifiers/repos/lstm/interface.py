import torch
import torch.optim as optim
from utils.model import initilize_lstm_model
from utils.tools import load_word2idx, predict


class LSTMInterface():
    def __init__(self, device, model_path, word2idx_path):
        super().__init__()
        self.device = device
        print('loading word2idx...')
        self.word2idx = load_word2idx(word2idx_path)
        self.model, _ = initilize_lstm_model(self.device, vocab_size=len(
            self.word2idx), embed_dim=300, dropout=0.5)
        self.model.load_state_dict(torch.load(
            model_path, map_location={'cuda:2': str(self.device)}))

    def get_score(self, payload):
        score = predict(self.model, self.word2idx, self.device, payload)
        if score is None:
            score = 1.0
        return score
