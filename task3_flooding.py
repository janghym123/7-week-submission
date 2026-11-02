"""Capacity-limited learning switch with frequency-aware admission.

Implements admission control and victim selection with a small, aging
Count-Min Sketch. Rare one-off sources do not evict frequently used stations.
"""
from zlib import crc32


class YourSwitch:
    BROADCAST = "ff:ff:ff:ff:ff:ff"
    SKETCH_ROWS = 4
    SKETCH_WIDTH = 2048
    DECAY_EVERY = 8192

    def __init__(self, ports, capacity):
        if ports < 0 or capacity < 0:
            raise ValueError("ports and capacity must be non-negative")
        self.ports = ports
        self.capacity = capacity
        self.table = {}                 # MAC -> output port
        self._last_seen = {}            # MAC -> most recent frame time
        self._sketch = [[0] * self.SKETCH_WIDTH for _ in range(self.SKETCH_ROWS)]
        self._observations = 0

    @staticmethod
    def _key(mac):
        return mac.encode("utf-8") if isinstance(mac, str) else bytes(mac)

    def _indices(self, mac):
        key = self._key(mac)
        # Distinct CRC seeds provide independent, deterministic sketch rows.
        return [crc32(key, 0x9e3779b9 * (row + 1)) % self.SKETCH_WIDTH
                for row in range(self.SKETCH_ROWS)]

    def _estimate(self, mac):
        return min(self._sketch[row][column]
                   for row, column in enumerate(self._indices(mac)))

    def _record(self, mac):
        for row, column in enumerate(self._indices(mac)):
            self._sketch[row][column] += 1

    def _decay(self):
        for row in self._sketch:
            for i, value in enumerate(row):
                row[i] = value // 2

    def _learn(self, src, in_port, now):
        if src in self.table:
            # Always trust current evidence, including a station moving ports.
            self.table[src] = in_port
            self._last_seen[src] = now
            return
        if self.capacity == 0:
            return
        if len(self.table) < self.capacity:
            self.table[src] = in_port
            self._last_seen[src] = now
            return

        # TinyLFU-style admission: a newcomer must be more popular than the
        # least valuable resident. Ties are declined to prevent one-hit churn.
        victim = min(self.table,
                     key=lambda mac: (self._estimate(mac), self._last_seen[mac]))
        if self._estimate(src) > self._estimate(victim):
            del self.table[victim]
            del self._last_seen[victim]
            self.table[src] = in_port
            self._last_seen[src] = now

    def handle(self, frame, in_port):
        src, dst, now = frame
        if not 0 <= in_port < self.ports:
            raise ValueError("in_port is outside the switch's ports")

        self._record(src)
        if dst != self.BROADCAST:
            self._record(dst)
        self._observations += 1
        if self._observations % self.DECAY_EVERY == 0:
            self._decay()

        self._learn(src, in_port, now)

        if dst == self.BROADCAST:
            candidates = range(self.ports)
        elif dst in self.table:
            candidates = (self.table[dst],)
        else:
            candidates = range(self.ports)
        return sorted(port for port in candidates if port != in_port)
