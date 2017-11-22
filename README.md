
seqr 
====
[![Build Status](https://travis-ci.org/macarthur-lab/seqr.svg?branch=master)](https://travis-ci.org/macarthur-lab/seqr)

seqr is a web-based analysis tool for rare disease genomics.

This repository contains the code that underlies the [Broad seqr instance](http://seqr.broadinstitute.org), as well as other seqr deployments.

## Overview

seqr consists of the following components or micro-services:
- seqr - the main client-server application - javascript + react.js on the client-side, python + django on the server-side.
- postgres - SQL database used by seqr and phenotips to store metadata and small reference datasets (eg. OMIM, clinvar).
- phenotips - 3rd-party web-based tool for entering structured phenotype information.
- mongo - NoSQL database used to store large variant datasets and reference data. This is being phased out in favor of elasticsearch.
- matchbox - a service that encapsulates communication with the Match Maker Exchange
- nginx - http server used as the main gateway between seqr and the internet.
- elasticsearch - NoSQL database that's replacing mongo as the database storing reference data and variant callsets in seqr.
- kibana - (optional) user-friendly visual interface to elasticsearch.


## Installation

We are now using Kubernetes for local, dev, and production deployments of seqr. This containerization layer allows reproducible, fully-scripted deployments and allows the same deployment scripts to work across operating systems (MacOSX, Linux or Windows), or cloud providers (minikube, Google, AWS, etc.)

For detailed installation steps, see:
* Kubernetes-based deployment: [deploy/kubernetes/README.md](deploy/kubernetes/README.md)

**Please Note:** seqr is still under active development, and undergoing refactoring. We suggest you contact us if you want to build on this repo.


## Related repositories

https://github.com/macarthur-lab/hail-elasticsearch-pipelines  
Dataset preprocessing pipelines used to annotate and load variant callsets into elasticsearch
