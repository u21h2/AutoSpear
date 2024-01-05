# WAFs

```
docker build -t waf/modsecurity:v1 classifiers/repos/modsecurity/
docker run -i -t -d -p 9000:80 --name=modsecurity  waf/modsecurity:v1
docker run -d -p 9000:80 --name=modsecurity  waf/modsecurity:v1 /usr/local/openresty/nginx/sbin/nginx -g "daemon off;"
docker exec -it modsecurity bash

docker build -t waf/wafbrain:v1 classifiers/repos/wafbrain/
docker run -p 9001:80 -d --name=wafbrain  waf/wafbrain:v1
docker exec -it wafbrain bash

docker build -t waf/cnn:v1 classifiers/repos/cnn/
docker run -p 9002:80 -d --name=cnn  waf/cnn:v1
docker exec -it cnn bash

docker build -t waf/lstm:v1 classifiers/repos/lstm/
docker run -p 9003:80 -d --name=lstm  waf/lstm:v1
docker exec -it lstm bash

curl http://0.0.0.0:9000/
curl -X POST -d "payload=benign" http://0.0.0.0:9000/waf
curl -X POST -d "payload=1' or 1 = 1" http://0.0.0.0:9000/waf
curl -X POST -d "payload=1) where (select 0) or 5232=5232 union all select null,null,null" http://0.0.0.0:9000/waf
curl -X POST -d "payload=1) where (select 0) or 5232=5232 union all /*foo*/ select null,null,null" http://0.0.0.0:9000/waf


curl http://0.0.0.0:9001/
curl -X POST -d "payload=benign" http://0.0.0.0:9001/waf
curl -X POST -d "payload=1' or 1 = 1" http://0.0.0.0:9001/waf

curl http://0.0.0.0:9002/
curl -X POST -d "payload=benign" http://0.0.0.0:9002/waf
curl -X POST -d "payload=1' or 1 = 1" http://0.0.0.0:9002/waf

curl http://0.0.0.0:9003/
curl -X POST -d "payload=benign" http://0.0.0.0:9003/waf
curl -X POST -d "payload=1' or 1 = 1" http://0.0.0.0:9003/waf
```


```
CN=false
if [[ $(echo "$(curl -s ipinfo.io)" | awk -F"[,:}]" '{for(i=1;i<=NF;i++){if($i~/'country'\042/){print $(i+1)}}}' | tr -d '"' | sed -n ${num}p) = ' CN' ]]; then CN=true; else CN=false ; fi
if [[ $CN = true ]]; then sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list; else echo 'no need to change origin';fi
if [[ $CN = true ]]; then sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list; else echo 'no need to change origin';fi

RUN if [[ $CN = true ]]; then pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ ; else echo 'no need to change origin';fi
```