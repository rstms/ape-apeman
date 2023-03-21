# wait for events emitted from a contract

import time

from ape_apeman import APE
from ape_apeman import json

SLEEP_INTERVAL=1

def handler(event):
    print(json.dumps(dict(event), hex_bytes=True))

def poll_events(contract_address):
    with APE() as ape:
        filter = ape.web3.eth.filter({'address': contract_address})
        while True:
            for event in filter.get_new_entries():
                handler(event)
            time.sleep(SLEEP_INTERVAL)

if __name__ == '__main__':
    poll_events('0xc1a0dCdddB744A06A155642d2F85C6184C27c915')
