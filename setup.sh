docker build -t madhush/ebpf-for-mac-python .
docker image push madhush/ebpf-for-mac-python:latest
kubectl apply -f depl.yaml
docker run -it --rm --privileged -p8000:8000 -v /lib/modules:/lib/modules:ro -v /etc/localtime:/etc/localtime:ro --pid=host ebpf-for-mac-python
