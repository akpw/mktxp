FROM python:3-alpine
LABEL org.opencontainers.image.source github.com/akpw/mktxp
WORKDIR /mktxp
COPY . .
RUN pip install ./ && apk add nano

# Patch routeros_api to support connection to IPv6 targets
RUN apk add patch && patch /usr/local/lib/python3.12/site-packages/routeros_api/api_socket.py < deploy/routeros_api_ipv6_patch.diff

EXPOSE 49090
RUN addgroup -S mktxp && adduser -S mktxp -G mktxp
USER mktxp
ENTRYPOINT ["/usr/local/bin/mktxp"]
CMD ["export"]
