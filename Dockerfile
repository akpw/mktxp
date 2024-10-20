FROM python:3-alpine
LABEL org.opencontainers.image.source github.com/akpw/mktxp
RUN addgroup -S mktxp && adduser -S mktxp -G mktxp
RUN apk add nano

WORKDIR /mktxp
COPY . .
RUN pip install ./

EXPOSE 49090

USER mktxp
ENTRYPOINT ["/usr/local/bin/mktxp"]
CMD ["export"]
