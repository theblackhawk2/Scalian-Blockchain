import sys
import getopt
import urllib.request
from urllib.error import HTTPError
from hashlib import sha512
import hashlib

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList





#Par defaut le validateur est le localhost

VALIDATOR_URL = "http://127.0.0.1"
LIST_PAYLOAD   =  ["","",""]


def utilisation():
    message = "Ce Script permet de lancer une requete xo vers un noeud specifique \n"
    message+="-h --host   : L'adresse du validateur sous la forme http://127.0.0.1\n"
    message+="-n --name   : Le nom du jeu a chercher \n"
    message+="-a --action : L'action a executer <create>, <take>, <delete>\n"
    message+="-s --space  : Le carreau sur lequel on execute l'action 0-9 \n"
    print(message)

def getParams():
    if len(sys.argv) == 1:
        utilisation()
        sys.exit(2) 
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"h:n:a:s:", ["host=", "name=", "action=", "space="])
    except getopt.GetoptError as err:
        print(err)
        utilisation()
        sys.exit(2)
    
    for option , arg in opts:
        if option in ("-h","--host"):
            global VALIDATOR_URL 
            VALIDATOR_URL   = arg
        elif option in ("-n", "--name"):
            LIST_PAYLOAD[0] = arg
        elif option in ("-a", "--action"):
            LIST_PAYLOAD[1] = arg
        elif option in ("-s", "--space"):
            LIST_PAYLOAD[2] = arg    

if __name__ == "__main__":

    getParams()
    # Instanciation d'un signataire aléatoire 
    context = create_context('secp256k1')
    
    private_key = context.new_random_private_key()
    
    signer = CryptoFactory(context).new_signer(private_key)
    
    payload_bytes = (',').join(LIST_PAYLOAD).encode()    
    
    txn_header_bytes = TransactionHeader(
        family_name='xo',
        family_version='1.1',
        inputs = [hashlib.sha512('xo'.encode()).hexdigest()[:6] + hashlib.sha512('game000'.encode()).hexdigest()[:64]],
        outputs = [hashlib.sha512('xo'.encode()).hexdigest()[:6] + hashlib.sha512('game000'.encode()).hexdigest()[:64]],
        signer_public_key=signer.get_public_key().as_hex(),
        # In this example, we're signing the batch with the same private key,
        # but the batch can be signed by another party, in which case, the
        # public key will need to be associated with that key.
        batcher_public_key=signer.get_public_key().as_hex(),
        # In this example, there are no dependencies.  This list should include
        # an previous transaction header signatures that must be applied for
        # this transaction to successfully commit.
        # For example,
        # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
        dependencies=[],
        payload_sha512=sha512(payload_bytes).hexdigest()
        ).SerializeToString()

    signature = signer.sign(txn_header_bytes)

    txn = Transaction(
        header=txn_header_bytes,
        header_signature=signature,
        payload=payload_bytes
    )

    txns = [txn]

    batch_header_bytes = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=[txn.header_signature for txn in txns],
    ).SerializeToString()

    signature = signer.sign(batch_header_bytes)

    batch = Batch(
        header=batch_header_bytes,
        header_signature=signature,
        transactions=txns
    )

    batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

    try:
        print("this is the"+VALIDATOR_URL)
        request = urllib.request.Request(
        VALIDATOR_URL + '/batches',
        batch_list_bytes,
        method='POST',
        headers={'Content-Type': 'application/octet-stream'})
        response = urllib.request.urlopen(request)

    except HTTPError as e:
        response = e.file
