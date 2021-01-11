# Distributed-Library
A virtual book library project to demonstrate a Fault-Tolerant Distributed Asynchronous System

This repo demonstrates several milestones as part of the course project of 18-749 Building Reliable Distributed Systems. The first milestone implements a simple client-server application with fault detection and heartbeats. The second milestone demonstrates an actively-replicated server with single fault and single-replica failover, while the third milestone involves a warm-passively replicated server with single fault, with primary failover to a backup. This project will demonstrate several core concepts of this class such as crash/message-loss faults, fault detection via heartbacks, active and passive replication with replica consistency, checkpointing, logging and duplicate detection. 

To run, simply run rm.py to launch the resource manager using the following command:

```
python rm.py --port 5008 --freq 0.1 --primary S1 --auto True --revive 1
```

The resource manger will trigger the launch of all server replicas, fault detectors, and clients. The clients are configured to send requests at a default rate of 10 messages per second.

