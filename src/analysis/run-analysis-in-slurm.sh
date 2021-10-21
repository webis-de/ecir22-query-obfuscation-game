#!/bin/bash -e

SRUN="srun --container-name=thesis-libera-analysis --container-image=ubuntu:20.04 --volume-mounts=/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/ --container-writable --pty -c 25 --mem=100G"

# The following lines are used to prepare the image, since I now have the image prepared on slurm, I commented them out.
#${SRUN} apt-get update
#${SRUN} apt-get install -y openjdk-11-jdk
#${RUN} pip3 install pyserini
#${RUN} pip3 install nltk
#${RUN} python3 -c 'import nltk; nltk.download("stopwords");'
#${RUN} python3 -c 'from nltk.corpus import stopwords; print(set(stopwords.words("english")));'

${RUN} bash -c "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/ python3 prepare_user_data.py"

