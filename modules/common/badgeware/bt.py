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
COMMAND_BADGECODE = 0xc0de
COMMAND_MESHCAST = 0xff00  # Anything starting 0xff__ should be rebroadcast


class BT:
    def __init__(self):
        self.messages = []
        self.badgecodes = {}
        self._seen = []
        self._timeout = None
        self._transmit_queue = []

        self._ble = bluetooth.BLE()
        self._ble.irq(self._irq)
        self._ble.active(True)

        self.address = binascii.hexlify(self._ble.config("mac")[1]).decode("ASCII")

    def send(self, command, data, destination=None, duration=30_000, interval=None):
        if self._timeout is not None:
            self._transmit_queue.append((command, data, destination, duration, interval))
            return

        destination_mac = destination or BROADCAST_ADDR
        interval = interval or 0.5
        command = int(command, 16) if isinstance(command, str) else command
        payload = struct.pack(">x6sH22s", binascii.unhexlify(destination_mac), command, data)
        self._ble.gap_advertise(int(interval * 1000 * 1000), adv_data=payload)
        if duration:
            if self._timeout:
                self._timeout.deinit()
            self._timeout = Timer()
            self._timeout.init(mode=Timer.ONE_SHOT, period=duration, callback=self._transmit_done, hard=False)

    def _transmit_done(self, _timer):
        self.stop()
        if self._transmit_queue:
            self.send(*self._transmit_queue.pop(0))

    def _see(self, crc):
        if crc not in self._seen:
            self._seen.append(crc)

    def broadcast(self, message, lifetime=10, duration=30_000, interval=None):
        # Make sure we track our own broadcasts as "seen" so we can filter them out
        self._see(binascii.crc32(message))
        self.send(COMMAND_MESHCAST | (lifetime & 0xff), message, BROADCAST_ADDR, duration, interval)

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
                dst_mac, command, message = struct.unpack(">x6sH22s", bytes(adv_data))
                dst_mac = binascii.hexlify(dst_mac).decode("ASCII")
                if dst_mac in (BROADCAST_ADDR, self.address):
                    if command == 0xc0de:
                        self.badgecodes[src_mac] = message[:6].decode("ASCII")
                    elif (command & COMMAND_MESHCAST) == COMMAND_MESHCAST:
                        lifetime = command & 0xff
                        crc = binascii.crc32(message)
                        if lifetime > 0 and crc not in self._seen:
                            lifetime -= 1
                            self.broadcast(message, lifetime)
                            self.messages.append((src_mac, dst_mac == BROADCAST_ADDR, f"{command & COMMAND_MESHCAST:02x}", message, crc))
                            self._see(crc)
                    else:
                        crc = binascii.crc32(adv_data)
                        if crc not in self._seen:
                            self.messages.append((src_mac, dst_mac == BROADCAST_ADDR, f"{command:02x}", message, crc))
                            self._see(crc)

    def unsee(self, message):
        crc = message[4] if isinstance(message, tuple) else message
        try:
            self._seen.remove(crc)
            return True
        except ValueError:
            return False  # cannot unsee

    def icon(self, pos, addr, size=8):
        icon = image(8, 8)
        icon.pen = color.rgb(0, 0, 0)
        icon.clear()
        icon.pen = color.rgb(255, 255, 255)
        seed = int(addr, 16) if isinstance(addr, str) else addr
        random.seed(seed)
        if seed & 2:
            _ = random.getrandbits(32)
        bits = random.getrandbits(32)
        a = (bits >> 24) & 0xff
        b = (bits >> 16) & 0xff
        c = (bits >> 8) & 0xff
        d = (bits >> 0) & 0xff
        for y in range(8):
            if a & (0b1 << y):
                icon.put(0, y)
                icon.put(7 - 0, y)
            if b & (0b1 << y):
                icon.put(1, y)
                icon.put(7 - 1, y)
            if c & (0b1 << y):
                icon.put(2, y)
                icon.put(7 - 2, y)
            if d & (0b1 << y):
                icon.put(3, y)
                icon.put(7 - 3, y)
        screen.blit(icon, icon.clip, rect(pos.x, pos.y, size, size))


builtins.bt = BT()
