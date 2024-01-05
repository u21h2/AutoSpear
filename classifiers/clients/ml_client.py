import requests


class MLClient:
    def __init__(self, base_url, thresh, blackbox=False):
        self.thresh = thresh
        self.blackbox = blackbox
        self.base_url = base_url

    def get_score(self, payload):
        resp = requests.post(url=self.base_url, data={'payload': payload})
        score = int(resp.json()['score'] > self.thresh) if self.blackbox else resp.json()['score']
        return score

    def get_thresh(self):
        return self.thresh



def main():
    clsf = MLClient(base_url='http://127.0.0.1:9002/waf', thresh=0.5)
    print(clsf.get_score(payload='admin or 1=1'))
    print(clsf.get_score(payload='Admin or 1=1'))
    print(clsf.get_score(payload='adMMin or 1=1'))
    print(clsf.get_score(payload='admin /**/or 1=1'))
    print(clsf.get_score(payload='admin or 1=1 --+'))
    print(clsf.get_score(payload='1"admin or 1=1'))
    print(clsf.get_score(payload='admin or 1=1'))
    print(clsf.get_score(payload='admin or 1=1'))
    print(clsf.get_score(payload='admin or 1=1'))
    print(clsf.get_score(payload='admin or 1=1'))


if __name__ == '__main__':
    main()
