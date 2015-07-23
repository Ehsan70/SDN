<b>Goal</b>: Setting up a custom topo. 

<b>Dependencies</b>: This tutorial only uses `Simple_Pkt_Topo.py` from the repo.

<b>Environment: </b> I have used the VM from sdn hub, I recommond you do the same. Link for installation is provided below: http://sdnhub.org/tutorials/sdn-tutorial-vm/

<b>Notations: </b>
 - `>` means the linuc command line <br>
 - `mininet>` means the mininet command line

# Start the network: 
In order to start the network you only need to run the command `sudo -E python <filename>`
which in our case would be:
```
sudo -E python Simple_Pkt_Topo.py
```
When you run that you should see: 

```
ubuntu@sdnhubvm:~/code/SDN[12:49] (master)$ sudo -E python Simple_Pkt_Topo.py 
Unable to contact the remote controller at 0.0.0.0:6633
*** Creating network
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 s2 s3 s4 
*** Adding links:
(h1, s1) (h2, s2) (h3, s3) (h4, s4) (s1, s2) (s1, s3) (s1, s4) 
*** Configuring hosts
h1 (cfs -1/100000us) h2 (cfs -1/100000us) h3 (cfs -1/100000us) h4 (cfs -1/100000us) 
*** Starting controller
c 
*** Starting 4 switches
s1 s2 s3 s4 ...
*** Starting CLI:
mininet> 

```
> Note that since you have not started any controller, the `pingall` is failing. 
  ```
  mininet> pingall
  *** Ping: testing ping reachability
  h1 -> X X X 
  h2 -> X X X 
  h3 -> X X X 
  h4 -> X X X 
  *** Results: 100% dropped (0/12 received)
  mininet> 
  ```
