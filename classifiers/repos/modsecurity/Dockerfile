FROM ubuntu

# CN
# RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
# RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.tuna\.tsinghua\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/security\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.zju\.edu\.cn\/ubuntu\//g' /etc/apt/sources.list

RUN apt update -y
RUN apt-get install apt-utils libpcre3-dev libssl-dev perl zlib1g-dev make build-essential curl git libtool autoconf automake -y

RUN mkdir /root/pkgs/

COPY coreruleset-3.3.2.tar.gz /root//pkgs/
COPY modsecurity-v3.0.6.tar.gz /root/pkgs/
COPY openresty-1.19.9.1.tar.gz /root/pkgs/
COPY modsecurity-nginx-v1.0.2.tar.gz /root/pkgs/
COPY nginx.conf /root/pkgs/
COPY modsecurity.conf /root/pkgs/

WORKDIR /root/pkgs/
RUN tar -zxvf openresty-1.19.9.1.tar.gz
RUN tar -zxvf modsecurity-v3.0.6.tar.gz
RUN tar -zxvf coreruleset-3.3.2.tar.gz
RUN tar -zxvf modsecurity-nginx-v1.0.2.tar.gz


# modsecurity
WORKDIR /root/pkgs/modsecurity-v3.0.6/
RUN ./configure
RUN make -j2
RUN make install


# openresty(nginx)
WORKDIR /root/pkgs/openresty-1.19.9.1/
RUN ./configure  --add-module=/root/pkgs/modsecurity-nginx-v1.0.2
RUN make -j2
RUN make install
RUN /usr/local/openresty/nginx/sbin/nginx -t

# rules
RUN mkdir /usr/local/openresty/nginx/conf/modsecurity/
RUN cp /root/pkgs/modsecurity-v3.0.6/modsecurity.conf-recommended /usr/local/openresty/nginx/conf/modsecurity/modsecurity.conf
RUN cp /root/pkgs/modsecurity-v3.0.6/unicode.mapping /usr/local/openresty/nginx/conf/modsecurity/unicode.mapping
RUN cp -r /root/pkgs/coreruleset-3.3.2/rules/ /usr/local/openresty/nginx/conf/modsecurity/
RUN cp /root/pkgs/coreruleset-3.3.2/crs-setup.conf.example /usr/local/openresty/nginx/conf/modsecurity/crs-setup.conf
RUN mv /usr/local/openresty/nginx/conf/modsecurity/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example  /usr/local/openresty/nginx/conf/modsecurity/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
RUN mv /usr/local/openresty/nginx/conf/modsecurity/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example /usr/local/openresty/nginx/conf/modsecurity/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
RUN mv /usr/local/openresty/nginx/conf/modsecurity/rules/REQUEST-910-IP-REPUTATION.conf /usr/local/openresty/nginx/conf/modsecurity/rules/REQUEST-910-IP-REPUTATION.conf.bak

RUN cp /root/pkgs/modsecurity.conf /usr/local/openresty/nginx/conf/modsecurity/modsecurity.conf
RUN cp /root/pkgs/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

EXPOSE 80

RUN /usr/local/openresty/nginx/sbin/nginx -t

CMD ["/usr/local/openresty/nginx/sbin/nginx","-g","daemon off;"]