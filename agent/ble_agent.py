import asyncio
import socket
import json
import base64
import argparse
from bleak import BleakScanner, AdvertisementData
from typing import Dict

class BleScanner:
    def __init__(self, host: str, port: int = 5038, scan_interval: int = 100, verbose: bool = False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.scan_interval = scan_interval
        self.verbose = verbose

    def convert_bytes_to_base64(self, data: Dict[int, bytes]) -> Dict[int, str]:
        return {key: base64.b64encode(value).decode("utf-8") for key, value in data.items()}

    async def handle_discovered_device(self, device, advertisement_data: AdvertisementData):
        device_info = {
            "address": device.address,
            "name": advertisement_data.local_name,
            "rssi": advertisement_data.rssi,
            "manufacturer_data": self.convert_bytes_to_base64(advertisement_data.manufacturer_data),
            "service_data": self.convert_bytes_to_base64(advertisement_data.service_data),
            "service_uuids": advertisement_data.service_uuids,
            "tx_power": advertisement_data.tx_power,
        }

        if self.verbose:
            print(json.dumps(device_info, indent=2))
            print("-" * 20)

        self.sock.sendto(json.dumps(device_info).encode('utf-8'), (self.host, self.port))

    async def scan_ble_devices(self):
        scanner = BleakScanner(detection_callback=self.handle_discovered_device, scanning_mode="active")

        try:
            while True:
                await scanner.start()
                await asyncio.sleep(self.scan_interval)
                await scanner.stop()
        except KeyboardInterrupt:
            print("Scan interrupted by the user.")
        finally:
            await scanner.stop()

def main():
    parser = argparse.ArgumentParser(description="BLE Scanner")
    parser.add_argument("-H", "--host", type=str, help="UDP server host")
    parser.add_argument("-p", "--port", type=int, default=5038, help="UDP server port")
    parser.add_argument("-i", "--scan_interval", type=int, default=10000, help="Scan interval in seconds")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print ble information")

    args = parser.parse_args()

    if not args.host:
        parser.error("Please provide the host.")

    scanner = BleScanner(host=args.host, port=args.port, scan_interval=args.scan_interval, verbose=args.verbose)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scanner.scan_ble_devices())

if __name__ == "__main__":
    main()

