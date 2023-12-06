# cmu_18749

checkout this [link](https://docs.google.com/document/d/1fr6UlXmZ4OmYD6f2gfefS0EmnmWwcWCjtbjEaJdLPbI/edit)

## Instructions

Replica Manager: (active)
- python rm.py -r RM --active

Replica Manager: (passive)
- python rm.py -r RM

Global Fault Detector:
- python gfd.py -g gfd

Local Fault Detector:
- python lfd.py -l L1 -s S1 -hb 5

Server (active):
- python server.py -s S1 -p 7777 --active
- python server.py -s S2 -p 8888 --active --recover
- python server.py -s S3 -p 9999 --active --recover

Server (passive):
- python server.py -s S1 -p 7777
- python server.py -s S2 -p 8888
- python server.py -s S3 -p 9999

Client:
- python client.py -c C1
