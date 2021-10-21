#!/bin/bash -e

srun \
	--mem=100G -c 5 \
	--container-image=jupyter/datascience-notebook \
	--container-writable \
	--container-name=jupyter-libera \
	--container-mounts=${PWD}:/home/jovyan/work,/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera,/mnt/ceph/storage/data-tmp/2021/kibi9872/.ir_datasets:/root/.ir_datasets \
	jupyter notebook --ip 0.0.0.0 --allow-root

