import sys
import getopt
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler
from asset_handler import *
from asset_payload import * 
from asset_state   import *

"""
Enable argv command passing , to specify the url of the validator
in order to conect to it
"""


def main(validator_url):
    # In docker, the url would be the validator's container name with port 4004
    
    processor = TransactionProcessor(url=validator_url)

    handler = AssetTransactionHandler(ASSET_NAMESPACE)

    processor.add_handler(handler)

    processor.start()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage : python3 asset-tp.py -C <host>")
        sys.exit(2) 
        
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"C:", ["connect="])
    except getopt.GetoptError as err:
        print(err)
        utilisation()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-C", "--connect"):
            main(arg)
        else:
            sys.exit(2)

