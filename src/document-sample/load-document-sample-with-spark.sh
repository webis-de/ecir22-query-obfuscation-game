#!/bin/bash -e

# see https://github.com/verAPPelt/AutomatischeVerschleierung/blob/integration-tests/JufoGradle/src/main/java/spark/SparkExtractDocumentsForCollection.java
JAR_FILE=/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/resources/JufoGradle-all.jar

spark-submit \
        --conf "spark.speculation=true" \
        --conf "spark.speculation.interval=5000ms" \
        --conf "spark.speculation.multiplier=5" \
        --conf "spark.speculation.quantile=0.90" \
        --conf "spark.dynamicAllocation.maxExecutors=75" \
        --conf "spark.yarn.maxAppAttempts=1" \
        --deploy-mode cluster \
        --class spark.SparkExtractDocumentsForCollection \
        --conf spark.default.parallelism=5000\
        --executor-cores 1\
        --num-executors 40\
        --driver-memory 15G\
        --executor-memory 10G\
        ${JAR_FILE} \
		--input file:///mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/document-sample/random-document-sample-arampatzis-approach/data100.csv
		--index cw12
		--output thesis-libera/document-sample-data-100.jsonl

