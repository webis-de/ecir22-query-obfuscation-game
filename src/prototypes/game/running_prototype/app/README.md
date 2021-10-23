# Flask Server Setup

### Step-By-Step List

- Install requirements: Run `pip3 install -r requirements.txt (Python 3)`
- Run `export FLASK_APP=flask_server`. If there is a problem with the JAVA_HOME setting \
  use `export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` to fix it
- Run `flask run`
- It could be possible that the index has to be created beforehand. If this is the case see the README.md in \
  the /src/document-samle/ folder and follow it's content.

### Production Logs

```
kubectl -n webisstud logs pod/wstud-thesis-libera-6f6448fc9f-7g2x6 -c wstud-thesis-libera
```

### Deployment 

Build the docker image:
```
docker build -t mam10eks/tmp-l-p:0.0.11 .
docker tag mam10eks/tmp-l-p:0.0.11 mam10eks/tmp-l-p:latest
```

Push the docker image:

```
docker login
docker push mam10eks/tmp-l-p:0.0.11
docker push mam10eks/tmp-l-p:latest
```

```
docker run --rm -ti --net=host mongo:4.4
```

```
docker run --rm -ti --net=host -v /home/maik/workspace/finalize-tables-cikm2020/copycat-spark/src/main/jupyter/index-robust04-20191213/:/lucene-index/ -v ${PWD}/tmp-docker-config.py:/app/config.py mam10eks/tmp-l-p:latest flask run --host 0.0.0.0
```

Deploy it in kubernetes:

```
kubectl -n webisstud apply -f game-k8s.yml
kubectl -n webisservices apply -f
```

```
kubectl -n services-demos create configmap city-of-disguise-config --from-file=city-of-disguise-config.py
```

