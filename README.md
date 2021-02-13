# Terminology Builder (term-builder)

A collection of various utilities aiming ontology management and UMLS connectivity. Application requires a UMLS database in MySQL.

  * `genOBO.sh` It generates an subset of UMLS in OBO format, using `generateOBO.py`. Please, type
  
        python2 ./generateOBO.py --help
      
     for complete application options.
     
  * `esIndex.py`: Generates an UMLS index on Elasticsearch. Please, type
  
        python2 ./esIndex.py --help
      
     for complete application options. A sample configuration set is available in `esIndex.txt`.
