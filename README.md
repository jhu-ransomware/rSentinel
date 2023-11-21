# rSentinel: Distributed Ransomware Defence System

## Introduction

## Configuration

### Node Count Configuration
Filename - constants.py
This file needs to have the total number of nodes in the network. For example, let's say we have 3 nodes in the network - Node 0 (10.0.0.4), Node 1 (10.0.0.5), Node 2 (10.0.0.6).  

```
NUM_NODES = 3
```

### Nodes Configurations
Filename - connections.txt  
This file needs to have the IP addresses of the remaining nodes in the network. For example, let's say we have 3 nodes in the network - Node 0 (10.0.0.4), Node 1 (10.0.0.5), Node 2 (10.0.0.6).  

Node 0 **connections.txt** -
```
2  
1 10.0.0.5  
2 10.0.0.6  
```
Node 1 **connections.txt** -
```
2  
0 10.0.0.4  
2 10.0.0.6  
```
Node 2 **connections.txt** -
```
2  
0 10.0.0.4  
1 10.0.0.5  
```
asdasd  
asdasd

## Setup and requirements

## License

## Contact Us
