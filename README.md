# rSentinel: Distributed Ransomware Defence System

## Introduction

## Installation
1. Clone the repository to your local machine  
```
git clone https://github.com/jhu-ransomware/rSentinel
```
2. Navigate to the rSentinel directory:
```
cd rSentinel
```

## Configuration

### CA

First, deploy [Baby CA](https://github.com/Crane-Mocker/Baby-CA) as your CA. Generate your private key and CA pem. 

Configure `allowed_ips` of *Baby CA*, put the IPs of your nodes here!

Transmit your CA pem to each of the node.

### Node CA Config

Config `CA_addr` and `ca_pem_path`, etc in `adaptive` module.

Config `hostnames` in `communication` module. The `hostname` for each node should match the CSR/Cert.

```
hostnames = {
    <Node 1 IP> : <Node 1 hostname or IP>,
    <Node 2 IP> : <Node 2 hostname or IP>,
    <Node 3 IP> : <Node 3 hostname or IP>
}
```

Config the CSR in `crypto.py`.


### Node Count Configuration
Location (Filename) - constants.py
This file needs to have the total number of nodes in the network. For example, let's say we have 3 nodes in the network - Node 0 (10.0.0.4), Node 1 (10.0.0.5), Node 2 (10.0.0.6).  

```
NUM_NODES = 3
```

### Node IP Address Configuration
Location (Filename) - connections.txt  
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

### Code Integrity Calculation
Location (Environment Variable Name) - RSENTINEL_COMBINED_HASH  
The Code Integrity Check is performed by generating a combined SHA-256 hash of all Python files within a specified directory, followed by signing this hash with a private RSA key. Below are the steps to generate and store hash values to verify code integrity -
1. Generate hash value using the python code -  
```
python code_integrity_check.py
```
2. The output of the above includes a Combined Hash value -
```
python .\code_integrity_check.py
Combined Hash: f50a4dd5436579c528492ca17b7696363e9d3f6efd99257fa3fd48f246a77830
Signature: 3c25d53290bf2634bdc71f88e5a6d866d43e89f7f8c376667cff33d862dbeb5084c86307451d1b3731f44ac149a307ea7790c22776bcaa4a1de350355559555738f159e2de6a6364fd7182efe0873742e62463b26b269a443da04d5c45ee49a79c21fbfc5335dffe6921d1c675191c67df02df2a4d3182e111444fbfda1d824cc501ed12ad0c17680a7b1f1e3caecbb71be463ac95ec0a4b1d336fa6e6a91d470a0bac872ef40a67fb816f7d06f0c02cc9c1da8ab928fc57741dcace5b563fae78d9508a781f4cb573f7654f5fc702884a93e90b8b83f6fdfba3ac27660063746095fd7f4e1a7a74c64b091e1bf74551dda5921620d7cc2d970b08169a43982e
2023-11-21 00:53:35 - INFO: Verification Succeeded
Signature is valid: True
```
3. Use the hash value and store in the environment variable. This will need to be changed in further iterations to store the hash value in a secure location like vault.
```
setx RSENTINEL_COMBINED_HASH "f50a4dd5436579c528492ca17b7696363e9d3f6efd99257fa3fd48f246a77830" /M
```

## Execution

To use *Baby CA* with *rSentinel*, start *Baby CA* in flag mode: 

```bash
python Baby-CA.py -f
```

To run rSentinel on a node, use the following command format. You can specify the node number and its fault status.

Below are examples of running the tool with a fault status of 0.

**Node 0** -
```
python p2p.py -n 0 -f 0
```
OR
```
python p2p.py --this_node 0 --fault_status 0
```

**Node 1** -
```
python p2p.py -n 1 -f 0
```
OR
```
python p2p.py --this_node 1 --fault_status 0
```


**Node 2** -
```
python p2p.py -n 2 -f 0
```
OR
```
python p2p.py --this_node 2 --fault_status 0
```
## License

## Contact Us
