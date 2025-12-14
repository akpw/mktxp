FROM python:3-alpine

LABEL org.opencontainers.image.source=https://github.com/akpw/mktxp
LABEL org.opencontainers.image.description="MKTXP is a Prometheus Exporter for Mikrotik RouterOS devices"
LABEL org.opencontainers.image.licenses=GPLv2+

RUN adduser -u 1000 -D mktxp
RUN apk add nano

# Create standard config directory with proper ownership
RUN mkdir -p /etc/mktxp && chown mktxp:mktxp /etc/mktxp

WORKDIR /mktxp
COPY . .
RUN pip install ./

EXPOSE 49090

USER mktxp
ENV PYTHONUNBUFFERED=1
CMD ["mktxp", "export"]
