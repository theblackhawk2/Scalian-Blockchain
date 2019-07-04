import sys
import getopt
import urllib.request
import hashlib

from hashlib import sha512
from urllib.error import HTTPError
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList

#Par defaut le validateur est le localhost

VALIDATOR_URL = "http://127.0.0.1"
LIST_PAYLOAD   =  ["","","",""]


def utilisation():
    message = "Ce Script permet de lancer une requete asset vers un noeud specifique \n"
    message+= "Utilisation python asset_client.py [opts] [args]"
    message+="-h --host   : L'adresse du validateur sous la forme http://127.0.0.1\n"
    message+="-n --name   : Le nom de bien recherche \n"
    message+="-s --serie  : Le numero de serie du bien (Identification unique)\n"
    message+="-a --action : L'action a executer <create>, <transfer>, <destroy>\n"
    message+="-d --dest   : La cle publique du nouveau destinataire (New Owner)"
    print(message)

def getParams():
    global VALIDATOR_URL 
    global LIST_PAYLOAD

    if len(sys.argv) == 1:
        utilisation()
        sys.exit(2) 
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"h:n:s:a:d:", ["host=", "name=", "serie=", "action=","dest="])
    except getopt.GetoptError as err:
        print(err)
        utilisation()
        sys.exit(2)
    
    for option , arg in opts:
        if option in ("-h","--host"):
            VALIDATOR_URL   = arg
        elif option in ("-n", "--name"):
            LIST_PAYLOAD[0] = arg
        elif option in ("-s", "--serie"):
            LIST_PAYLOAD[1] = arg 
        elif option in ("-a", "--action"):
            LIST_PAYLOAD[2] = arg
        elif option in ("-d","--dest"):
            LIST_PAYLOAD[3] = arg
           

if __name__ == "__main__":

    getParams()
    # Instanciation d'un signataire aléatoire 
    context = create_context('secp256k1')
    
    private_key = context.new_random_private_key()
    
    signer = CryptoFactory(context).new_signer(private_key)
    
    payload_bytes = (',').join(LIST_PAYLOAD).encode()    
    
    txn_header_bytes = TransactionHeader(
        family_name='asset',
        family_version='1.0',
        inputs = [hashlib.sha512('asset'.encode()).hexdigest()[:6] + hashlib.sha512(LIST_PAYLOAD[1].encode()).hexdigest()[:64]],
        outputs = [hashlib.sha512('asset'.encode()).hexdigest()[:6] + hashlib.sha512(LIST_PAYLOAD[1].encode()).hexdigest()[:64]],
        signer_public_key=signer.get_public_key().as_hex(),
        batcher_public_key=signer.get_public_key().as_hex(),
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
        print("Envoi de la requete a l'adresse : "+VALIDATOR_URL)
        request = urllib.request.Request(
        VALIDATOR_URL + '/batches',
        batch_list_bytes,
        method='POST',
        headers={'Content-Type': 'application/octet-stream'})
        response = urllib.request.urlopen(request)

    except HTTPError as e:
        response = e.file
