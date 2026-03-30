import bluetooth
import binascii
import struct
import builtins
import random
from machine import Timer


_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

DURATION_MS = 0
INTERVAL_US = int(.2 * 1000 * 1000)
WINDOW_US   = int(.2 * 1000 * 1000)
BROADCAST_ADDR = "28cdc1ffffff"


class BT:
    def __init__(self):
        self.messages = []
        self.badgecodes = {}
        self._seen = []
        self._timeout = None

        self._ble = bluetooth.BLE()
        self._ble.irq(self._irq)
        self._ble.active(True)

        self.address = binascii.hexlify(self._ble.config("mac")[1]).decode("ASCII")

    def send(self, command, data, destination=None, duration=30_000, interval=None):
        destination_mac = destination or BROADCAST_ADDR
        interval = interval or 0.5
        command = int(command, 16) if isinstance(command, str) else command
        payload = struct.pack(">x6sH22s", binascii.unhexlify(destination_mac), command, data)
        self._ble.gap_advertise(int(interval * 1000 * 1000), adv_data=payload)
        if duration:
            if self._timeout:
                self._timeout.deinit()
            self._timeout = Timer()
            self._timeout.init(mode=Timer.ONE_SHOT, period=duration, callback=self.stop)

    def stop(self):
        if self._timeout:
            self._timeout.deinit()
            self._timeout = None
        self._ble.gap_advertise(None)

    def badgecode(self, code):
        self.send(0xc0de, code)

    def find(self, badgecode):
        return tuple(k for k, v in filter(lambda kv: kv[1] == badgecode, self.badgecodes.items()))

    def listen(self):
        self._ble.gap_scan(DURATION_MS, INTERVAL_US, WINDOW_US, False)

    def stop_listening(self):
        self._ble.gap_scan(None)

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, src_mac, adv_type, rssi, adv_data = data
            src_mac = binascii.hexlify(src_mac).decode("ASCII")

            if len(adv_data) == 31:
                crc = binascii.crc32(adv_data)
                dst_mac, command, message = struct.unpack(">x6sH22s", bytes(adv_data))
                dst_mac = binascii.hexlify(dst_mac).decode("ASCII")
                if dst_mac in (BROADCAST_ADDR, self.address):
                    if command == 0xc0de:
                        self.badgecodes[src_mac] = message[:6].decode("ASCII")
                    else:
                        if crc not in self._seen:
                            self.messages.append((src_mac, dst_mac == BROADCAST_ADDR, f"{command:02x}", message, crc))
                            self._seen.append(crc)

    def unsee(self, message):
        crc = message[4] if isinstance(message, tuple) else message
        try:
            self._seen.remove(crc)
            return True
        except ValueError:
            return False  # cannot unsee

    def icon(self, pos, addr):
        seed = int(addr, 16)
        random.seed(seed)
        if seed & 2:
            _ = random.getrandbits(32)
        bits = random.getrandbits(32)
        a = (bits >> 24) & 0xff
        b = (bits >> 16) & 0xff
        c = (bits >> 8) & 0xff
        d = (bits >> 0) & 0xff
        o_x = pos.x + 1
        o_y = pos.y
        for y in range(8):
            if a & (0b1 << y):
                screen.put(o_x + 0, o_y + y)
                screen.put(o_x + 7 - 0, o_y + y)
            if b & (0b1 << y):
                screen.put(o_x + 1, o_y + y)
                screen.put(o_x + 7 - 1, o_y + y)
            if c & (0b1 << y):
                screen.put(o_x + 2, o_y + y)
                screen.put(o_x + 7 - 2, o_y + y)
            if d & (0b1 << y):
                screen.put(o_x + 3, o_y + y)
                screen.put(o_x + 7 - 3, o_y + y)


builtins.bt = BT()
