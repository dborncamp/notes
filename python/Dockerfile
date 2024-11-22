#
# Builder image, build a binary to be shipped off to a different base
#
FROM registry-gitlab.aero.ball.com/bsf/runner-images/ubi9/ubi:9.2 as builder

WORKDIR /opt/app

ADD . .

RUN dnf install -y \
        python3.11 \
        binutils \
        patchelf

RUN python3.11 -m venv tester_env &&\
    # python3.11 -m ensurepip --upgrade &&\
    source tester_env/bin/activate && \
    pip install --upgrade setuptools pip build pyinstaller staticx && \
    pip install -r requirements.txt && \
    pip install . && \
    pyinstaller --noconsole --onefile --name network_tester --hidden-import aioudp --add-binary="/usr/lib64/libz.so.1:." src/network_tester/main.py && \ 
    mkdir -p /opt/app/static/ && \ 
    staticx /opt/app/dist/network_tester /opt/app/static/network_tester 


#
#
# A release image based on SMS's UBI 9.
# This container is WAY bigger than it needs to be
#
#
FROM registry-gitlab.aero.ball.com/bsf/runner-images/ubi9/ubi:9.2 as release-ubi9

WORKDIR /opt/app

COPY --from=builder /opt/app/static/network_tester /opt/app/network_tester

CMD /opt/app/network_tester

#
#
# A release image based on distroless. Much smaller...
#
#

FROM gcr.io/distroless/static-debian12 as release

WORKDIR /

COPY --from=builder /opt/app/static/network_tester /

ENTRYPOINT [ "/network_tester" ]


FROM builder as tester

CMD source tester_env/bin/activate && src/network_tester/bonus.py