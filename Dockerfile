FROM docker/for-desktop-kernel:5.10.47-0b705d955f5e283f62583c4e227d64a7924c138f AS ksrc
FROM ubuntu:latest

WORKDIR /
COPY --from=ksrc /kernel-dev.tar /
RUN tar xf kernel-dev.tar && rm kernel-dev.tar

RUN apt-get update && apt install -y vim kmod python3-bpfcc

COPY hello_world.py /root
WORKDIR /root
CMD mount -t debugfs none /sys/kernel/debug && /bin/bash
