import numpy as np
import torch
import json
from nltk.tokenize import word_tokenize
from tqdm import tqdm_notebook
import torch.nn.functional as F


def split_word_tokenize(text):
    def trim_string(x):
        splits = '=|,'
        trimed = ''
        x = str(x)
        for idx, char in enumerate(str(x)):
            if char in splits:
                try:
                    if trimed[-1] != ' ':
                        trimed += ' '
                except:
                    pass
                trimed += char
                try:
                    if x[idx+1] != ' ':
                        trimed += ' '
                except:
                    pass
            else:
                trimed += char
        return trimed
    text = trim_string(text)
    return word_tokenize(text)


def encode(tokenized_texts, word2idx, max_len):
    """Pad each sentence to the maximum sentence length and encode tokens to
    their index in the vocabulary.

    Returns:
        input_ids (np.array): Array of token indexes in the vocabulary with
            shape (N, max_len). It will the input of our CNN model.
    """

    input_ids = []
    for tokenized_sent in tokenized_texts:
        # Pad sentences to max_len
        tokenized_sent += ['<pad>'] * (max_len - len(tokenized_sent))

        # Encode tokens to input_ids
        input_id = [word2idx.get(token, word2idx['<unk>']) for token in tokenized_sent]
        input_ids.append(input_id)

    return np.array(input_ids)


def load_pretrained_vectors(word2idx, fname):
    """Load pretrained vectors and create embedding layers.

    Args:
        word2idx (Dict): Vocabulary built from the corpus
        fname (str): Path to pretrained vector file

    Returns:
        embeddings (np.array): Embedding matrix with shape (N, d) where N is
            the size of word2idx and d is embedding dimension
    """

    print("Loading pretrained vectors...")
    fin = open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())

    # Initilize random embeddings
    embeddings = np.random.uniform(-0.25, 0.25, (len(word2idx), d))
    embeddings[word2idx['<pad>']] = np.zeros((d,))

    # Load pretrained vectors
    count = 0
    for line in tqdm_notebook(fin):
        tokens = line.rstrip().split(' ')
        word = tokens[0]
        if word in word2idx:
            count += 1
            embeddings[word2idx[word]] = np.array(tokens[1:], dtype=np.float32)

    print(f"There are {count} / {len(word2idx)} pretrained vectors found.")

    return embeddings






def predict(model, word2idx,device,text, max_len=128):
    """Predict probability that a review is positive."""
    # Tokenize, pad and encode text
    tokens = split_word_tokenize(text)
    # print(tokens)
    padded_tokens = tokens + ['<pad>'] * (max_len - len(tokens))
    input_id = [word2idx.get(token, word2idx['<unk>']) for token in padded_tokens]

    # Convert to PyTorch tensors
    input_id = torch.tensor(input_id).unsqueeze(dim=0).to(device)

    # Compute logits
    logits = model.forward(input_id)
    # print(logits)
    #  Compute probability
    probs = F.softmax(logits, dim=1).squeeze(dim=0)

    # print(f"This payload is {probs[1] * 100:.2f}% sqli.")

    return probs[1].item()


def load_word2idx(path):
    with open(path, 'r') as f:
        return json.load(f)
