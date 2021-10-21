# Indexing + Retrieval of a small example with Pyserini

See documentation here: https://github.com/castorini/pyserini

### Step-By-Step List

- Mount `/mnt/ceph/storage`
- run `./create-index.sh` to create the index. If there is a problem with the JAVA_HOME setting \
  use `export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64` to fix it
- Install requirements: `pip3 -r requirements.txt`
- Example for retrieval, run `./example.py`


### Sample of random documents (for some "background noise" of non-sensitive documents) 

The samples are located at: `/mnt/ceph/storage/data-in-progress/data-teaching/theses/wstud-thesis-libera/document-sample/random-document-sample-arampatzis-approach`

ToDo: Add description of the sampling strategy (we reuse the strategy by arampatzis).

```
python random-document-sample-arampatzis-approach.py [apikey] [first query] [indice] [k-value] [document count] [output-filename]
```

Example: `python random-document-sample-arampatzis-approach.py 1234-5678-9000 www cw09 10 50 data50`



