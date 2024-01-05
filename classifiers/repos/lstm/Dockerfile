FROM ubuntu

# CN
# RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
# RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN apt update -y
RUN apt install apt-utils python3 python3-pip wget curl unzip -y

RUN mkdir /root/waf
RUN mkdir /root/waf/utils
COPY interface.py /root/waf/
COPY requirements.txt /root/waf/
COPY server.py /root/waf/
COPY utils/model.py /root/waf/utils/
COPY utils/tools.py /root/waf/utils/
COPY utils/__init__.py /root/waf/utils/
COPY model.pt /root/waf/
COPY word2idx.json /root/waf/


RUN mkdir /root/nltk_data/
COPY punkt.zip /root/nltk_data/
WORKDIR /root/nltk_data/
RUN unzip punkt.zip -d tokenizers


# CN
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

WORKDIR /root/waf/
RUN pip3 install -r requirements.txt  --no-cache-dir --default-timeout=100
EXPOSE 80
CMD ["python3", "server.py"]

