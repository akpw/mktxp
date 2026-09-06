FROM python:3-alpine

LABEL org.opencontainers.image.source=https://github.com/akpw/mktxp
LABEL org.opencontainers.image.description="MikroTik RouterOS CLI Diagnostic Tool, GitOps Configuration Manager, and Prometheus Exporter"
LABEL org.opencontainers.image.licenses=GPLv2+

# Provision non-root user, editor, and config directory in a single layer to minimize image size
RUN adduser -u 1000 -D mktxp && \
    apk add --no-cache nano && \
    mkdir -p /etc/mktxp && \
    chown mktxp:mktxp /etc/mktxp

WORKDIR /mktxp
COPY . .
RUN pip install --no-cache-dir ./

EXPOSE 49090

USER mktxp
ENV PYTHONUNBUFFERED=1
ENV XDG_CONFIG_HOME=/etc
CMD ["mktxp", "export"]
