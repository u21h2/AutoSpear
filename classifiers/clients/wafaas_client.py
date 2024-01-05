import time
import json
import requests
from requests.adapters import HTTPAdapter


class WAFaasClient:
    def __init__(self, base_url, manner='GET(JSON)', sleep_time=0, intercept_status=403, cookie=''):
        self.sleep_time = sleep_time
        self.base_url = base_url
        self.intercept_status = intercept_status
        self.manner = manner
        self.headers = {
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        if self.manner == 'POST':
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif self.manner == 'POST(JSON)':
            self.headers['Content-Type'] = 'application/json'
        if cookie:
            self.headers['Cookie'] = cookie
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=3))
        self.s.mount('https://', HTTPAdapter(max_retries=3))

    def get_score(self, payload):
        time.sleep(self.sleep_time)
        if self.manner == 'GET':
            request_url = self.base_url + "?id=" + payload
            resp = self.s.get(url=request_url, headers=self.headers, timeout=5)  # max retry?
        elif self.manner == 'GET(JSON)':
            request_data = json.dumps({'id': payload})
            request_url = self.base_url + "?data=" + request_data
            resp = self.s.get(url=request_url, headers=self.headers, timeout=5)  # max retry?
        elif self.manner == 'POST':
            request_url = self.base_url
            request_data = {'id': payload}
            resp = self.s.post(url=request_url, data=request_data,
                               headers=self.headers, timeout=5)  # max retry?
        elif self.manner == 'POST(JSON)':
            request_url = self.base_url
            request_data = json.dumps({'id': payload})
            resp = self.s.post(url=request_url, data=request_data,
                               headers=self.headers, timeout=5)  # max retry?
        if resp.status_code == 200:
            res = 0
        elif resp.status_code == self.intercept_status:
            res = 1
        else:
            print(resp.status_code)
            raise Exception
        return res

    def get_thresh(self):
        return 0.5

    def set_blackbox(self):
        pass


def main():
    clsf = WAFaasClient(base_url="http://10.15.196.135:8088/vulnerabilities/sqli/",manner='GET',sleep_time=0, intercept_status=403)
    payloads = ["1 union all select null,null,null--",'15318901808','123.sql']
    for payload in payloads:
        print(payload)
        print(clsf.get_score(payload))


if __name__ == '__main__':
    main()
