#!/bin/bash -e

git submodule update --init --recursive
cd web-search-anserini-sandbox
mvn -DskipTests clean package appassembler:assemble

./target/appassembler/bin/IndexCollection \
	-collection LocalJsonlUuidChatNoirDocumentCollection \
	-input /mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/clueweb-documents-v1 \
	-index /mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/lucene-index.cw12-documents-v1.pos+docvectors \
	-generator JsoupGenerator \
	-threads 25 -storePositions -storeDocvectors
