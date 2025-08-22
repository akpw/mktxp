FROM python:3-alpine

LABEL org.opencontainers.image.source=https://github.com/akpw/mktxp
LABEL org.opencontainers.image.description="MKTXP is a Prometheus Exporter for Mikrotik RouterOS devices"
LABEL org.opencontainers.image.licenses=GPLv2+

RUN addgroup -S mktxp && adduser -S mktxp -G mktxp
RUN apk add nano

WORKDIR /mktxp
COPY . .
RUN pip install ./

EXPOSE 49090

USER mktxp
ENTRYPOINT ["/usr/local/bin/mktxp"]
ENV PYTHONUNBUFFERED=1
CMD ["export"]
