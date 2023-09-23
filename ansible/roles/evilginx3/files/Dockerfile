FROM golang:alpine

ENV INSTALL_PACKAGES="git make gcc musl-dev"
ENV EVILGINX_REPO="https://github.com/kgretzky/evilginx2.git"
ENV EVILGINX_DIR="/go/src/github.com/kgretzky/evilginx2"
ENV EVILGINX_BIN="/bin/evilginx"

RUN set -ex \
    && apk update \
    && apk add --no-cache ${INSTALL_PACKAGES} \
    && mkdir -p $(dirname ${EVILGINX_DIR}) \
    && git clone ${EVILGINX_REPO} ${EVILGINX_DIR} \
    && cd ${EVILGINX_DIR} \
    && go get ./... \
    && make \
    && mv build/evilginx ${EVILGINX_BIN} \
    && apk del ${INSTALL_PACKAGES} \
    && rm -rf /var/cache/apk/* /go/pkg /go/src

WORKDIR /opt/evilginx

CMD ["/bin/sh"]
#CMD ["evilginx", "-p", "/opt/evilginx/phishlets", "-c", "/opt/evilginx/config", "-developer"]
