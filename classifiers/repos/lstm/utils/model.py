import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch.optim as optim
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class LSTM_(nn.Module):
    def __init__(self,pretrained_embedding=None,freeze_embedding=False,vocab_size=None,
                 embed_dim=300,hidden_size=128,num_classes=2,dropout=0.5,training=False):
        super(LSTM_, self).__init__()
        # Embedding layer
        if pretrained_embedding is not None:
            self.vocab_size, self.embed_dim = pretrained_embedding.shape
            self.embedding = nn.Embedding.from_pretrained(pretrained_embedding,freeze=freeze_embedding)
        else:
            self.embed_dim = embed_dim
            self.embedding = nn.Embedding(num_embeddings=vocab_size,embedding_dim=self.embed_dim,padding_idx=0,max_norm=5.0)
        # Conv Network
        self.lstm = nn.LSTM(input_size=embed_dim,
                            hidden_size=hidden_size,
                            num_layers=1,
                            batch_first=True,
                            bidirectional=True)
        # Fully-connected layer and Dropout
        self.fc = nn.Linear(hidden_size*2, num_classes)
        self.drop = nn.Dropout(p=dropout)
        self.training = training
    def forward(self, input_ids):
        # print('input_ids.shape',input_ids.shape[1])
        text_emb = self.embedding(input_ids).float()

        x, (h_n,c_n) = self.lstm(text_emb)

        # 获取两个方向最后一次的output,进行concat
        output_fw = h_n[-2,:,:] # 正向最后一次输出
        output_bw = h_n[-1,:,:] # 反向最后一次输出
        output = torch.cat([output_fw,output_bw],dim=-1)
        # print('LSTM,x_fc.shape1',output.shape)
        if self.training:
            output = self.drop(output)
        # print(output)
        logits = self.fc(output)
        # print('LSTM,logits.shape2',logits.shape)
        return logits


def initilize_lstm_model(device,pretrained_embedding=None,freeze_embedding=False,vocab_size=None,embed_dim=300,hidden_size=128,num_classes=2,dropout=0.5,learning_rate=0.01,training=False):
    lstm_model = LSTM_(pretrained_embedding=pretrained_embedding,freeze_embedding=freeze_embedding,vocab_size=vocab_size,embed_dim=embed_dim,
    hidden_size=hidden_size,num_classes=num_classes,dropout=dropout,training=training)
    lstm_model.to(device)
    optimizer = optim.Adadelta(lstm_model.parameters(),lr=learning_rate,rho=0.95)
    return lstm_model, optimizer
