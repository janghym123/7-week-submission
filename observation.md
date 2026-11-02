# Observations — Week 7

## Task 1 · Learning switch
A frame sent back through its arrival port can loop back to the sender or be needlessly duplicated on that LAN segment; switches filter that port to prevent the loop. A switch floods unknown unicast frames because all ports may lead to the destination, while a router has a destination network route and drops when no route exists. Time-based aging can forget an active station during a quiet interval and can retain a departed one until timeout; more direct evidence would be an explicit link-down or station-disconnect event, which a basic Ethernet switch often does not receive per endpoint.

## Task 2 · ARP
The official UMass/Kurose-Ross 9th-edition Ethernet trace archive (`wireshark-traces-9e.zip`) is used for Part B because this environment could not read the local ARP table or expose the Wi-Fi capture interface. This is the published sample trace, not a live capture from this laptop. In the trace, frame 108 asks who has 128.119.247.1: Ethernet destination MAC is `ff:ff:ff:ff:ff:ff` (broadcast). Frame 109 replies to `c4:41:1e:75:b1:52`, the requester's MAC (unicast).

The trace contains 179 ARP packets (178 requests, 1 reply) over 12.287 seconds, about 874 per minute if linearly extrapolated; it does not provide a measured one-minute window or campus machine count. A remote web server is not in the ARP table because ARP resolves only the next-hop link-layer address on the local link; remote IP traffic is sent to the gateway's MAC.

Windows denied `netsh interface ip delete arpcache` because the command requires administrator rights. The subsequent `ping -n 3 192.168.0.1` succeeded (3/3 replies, 0% loss; 1, 3, and 1 ms). The user then saved `arp -a` to `C:\Windows\System32\arp-after.txt`; its contents were not included here, and no pre-ping snapshot was saved. Because the cache was not cleared, A2 cannot identify the first entry repopulated and A3 cannot compare before/after counts. The ping may have refreshed an existing gateway entry, but the table reflects prior network activity.

## Task 3 · Full switch table
The switch uses a 4-row, 2,048-counter Count-Min Sketch as a bounded, decaying popularity estimate. When full, it admits a new source only if its estimated frequency exceeds that of the least-frequent resident; otherwise it declines the admission. On the local Zipf(1.50) proxy workload this reduced wasted deliveries by 50.55% with zero missed deliveries; the provided course harness was absent, so these are not its official numbers.

An attacker could send frames with many forged source MAC addresses to fill the table and displace legitimate stations, causing unknown traffic to be flooded. A switch can limit learned MAC addresses per port, rate-limit learning, and alert or block when a port produces an unusual number of new source addresses.
