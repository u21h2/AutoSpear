FROM ubuntu

# CN
# RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
# RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN apt update -y
RUN apt install apt-utils python3 python3-pip -y

RUN mkdir /root/waf
COPY interface.py /root/waf/
COPY requirements.txt /root/waf/
COPY server.py /root/waf/
COPY waf-brain.h5 /root/waf/

# CN
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/



WORKDIR /root/waf/

RUN pip3 install -r requirements.txt --no-cache-dir --default-timeout=100

EXPOSE 80

CMD ["python3", "server.py"]

