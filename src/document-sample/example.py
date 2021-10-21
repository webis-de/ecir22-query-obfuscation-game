#!/usr/bin/env python3

from pyserini.search import SimpleSearcher

searcher = SimpleSearcher('web-search-anserini-sandbox/indexes/lucene-index.cw12.pos+docvectors/')

hits = searcher.search('hubble space telescope')

for i in range(0, 10):
    print(f'{i+1:2} {hits[i].docid:15} {hits[i].score:.5f}')

