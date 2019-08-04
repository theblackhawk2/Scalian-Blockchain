import sys
import getopt
import urllib.request
import hashlib
import json
from hashlib import sha512
from urllib.error import HTTPError
# Sawtooth Imports

from sawtooth_signing import create_context, CryptoFactory
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


# Ecpy imports 

from ecpy.curves           import Curve, Point
from ecpy.keys             import ECPublicKey, ECPrivateKey
from ecpy.eddsa            import EDDSA
from ecdsa.util            import randrange
from sympy.ntheory.factor_ import digits
from aes_encrypt           import *
from crypto_prim           import *
from copy import copy

#Par defaut le validateur est le localhost

VALIDATOR_URL  = "http://127.0.0.1"
LIST_PAYLOAD   =  ["","","","","",""]

def make_address(action, pubkey):
    ASSET_NAMESPACE = hashlib.sha512('secret_asset'.encode()).hexdigest()[0:6]
    return ASSET_NAMESPACE + hashlib.sha512(action.encode()).hexdigest()[:4] + hashlib.sha512(pubkey.encode()).hexdigest()[:60]

def utilisation():
    message = "Ce Script permet hashlib.sha512('secret_asset'.encode()).hexdigest()[0:6]de lancer une requete asset vers un noeud specifique \n"
    message+= "Utilisation python asset_client.py [opts] [args]\n"
    message+="-o --operation  : Quel type d'operations vous souhaitz faire ? write | read | share\n"
    message+="-h --host   : L'adresse du validateur sous la forme http://127.0.0.1\n"
    message+="-n --name   : Le nom de bien recherche \n"
    message+="-s --serie  : Le numero de serie du bien (Identification unique)\n"
    message+="-a --action : L'action a executer <create>, <transfer>, <destroy>\n"
    message+="-d --dest   : La cle publique du nouveau destinataire (New Owner)\n"
    message+="-x --secret : Le ficher des cles publiques de l'autorite de partage de secrets ( En points )"
    print(message)

def getParams():
    global VALIDATOR_URL 
    global LIST_PAYLOAD

    if len(sys.argv) == 1:
        utilisation()
        sys.exit(2) 
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"h:n:s:a:d:x:o", ["host=", "name=", "serie=", "action=","dest=", "secret=","operation="])
    except getopt.GetoptError as err:
        print(err)
        utilisation()
        sys.exit(2)
    print(opts)
    for option , arg in opts:
        if option in ("-h","--host"):
            VALIDATOR_URL   = arg
        elif option in ("-n", "--name"):
            LIST_PAYLOAD[0] = arg
        elif option in ("-s", "--serie"):
            LIST_PAYLOAD[1] = arg 
        elif option in ("-a", "--action"):
            LIST_PAYLOAD[2] = arg
        elif option in ("-x", "--secret"):
            LIST_PAYLOAD[3] = arg
        elif option in ("-d","--dest"):
            LIST_PAYLOAD[4] = arg
        elif option in ("-o", "--operation"):
            LIST_PAYLOAD[5] = arg
           
    print(VALIDATOR_URL)
if __name__ == "__main__":
    getParams()
    print(LIST_PAYLOAD)
    # Instanciation d'un signataire aléatoire 
    context = create_context('secp256k1')
    private_key = Secp256k1PrivateKey.from_hex('953c35fae67d072f6edab47612ce453e0af1b87c9bfc46b6f1108c6a7b61170d')
    signer      = CryptoFactory(context).new_signer(private_key)
    """
    Loading policy as text file 
    pubKey1 x1,y1,pv
    pubkey2 x2,y2,pv
    ......
    ......
    """
    print("This is the link "+LIST_PAYLOAD[3])    
    File        = open(LIST_PAYLOAD[3],"r")
    # Elimination clé privée et \n
    list_policy = [tuple(line.strip("\n").split(",")[:-1]) for line in File.readlines()]
    
    policy      = json.dumps({"members" : list_policy})

    TransactionPayload = {
        "policy" : [],
        "secret" : 0,
        "encryptedShares" : [],
        "polyCommitments" : [],
        "message"         : "",
        "encMessage"      : "",
        "Hc"              : ""
    }

    P = PVSS(0)
    # The base point for PVSS
    h = int(hashlib.sha256(policy.encode()).hexdigest(),16)*P.curve.generator
    # Creating secret shares for a (3,5) Threshold Scheme
    shares,polyCommit = P.secret_split(randrange(P.prime),3,5,h)
    # Creating the secret Message "Original Transaction"
    secretMessage     =  json.dumps({"from":signer.get_public_key().as_hex(),
                                               "to"  :LIST_PAYLOAD[4],
                                               "action":LIST_PAYLOAD[2],
                                               "serie":LIST_PAYLOAD[1] },sort_keys=True)
    
    encryptedShares   = []
    #Encrypt the shares (Starting from share 1) for each secret sharing member
    for i in range(len(list_policy)-1):
        key = list_policy[i]
        pk = ECPublicKey(Point(key[0],key[1],P.curve))
        R, cipher = P.encrypt(str(shares[i+1]),pk)
        encryptedShares.append(json.dumps({"index" : i,
                                          "for" : [pk.W.x,pk.W.y],
                                          "encrypted": [(R.x,R.y),cipher]},sort_keys=True))
    # Filling up the payload 
    TransactionPayload["secret"]          = shares[0]
    TransactionPayload["policy"]          = policy
    TransactionPayload["encryptedShares"] = encryptedShares
    TransactionPayload["polyCommitments"] = []
    for commit in polyCommit:
        TransactionPayload['polyCommitments'].append((commit.x,commit.y))

    TransactionPayload["message"]         = secretMessage
    TransactionPayload["encMessage"]      = P.symetric_encrypt(secretMessage,shares[0])
    TransactionPayload["h"]               = [h.x,h.y]
    TransactionPayload["secretShares"]    = shares[1:]
    TransactionPayload["Hc"]              = hashlib.sha256(TransactionPayload["encMessage"].encode()).hexdigest()

    LIST_PAYLOAD.append(json.dumps(TransactionPayload,sort_keys=True))

    # Gathering and encoding all data 
    print("adress lists" + str([make_address("write", pubkey[0]) for pubkey in list_policy]))
    payload_bytes = (';').join(LIST_PAYLOAD).encode()   
    txn_header_bytes = TransactionHeader(
        family_name='secret_asset',
        family_version='1.0',
        inputs = [make_address("write", pubkey[0]) for pubkey in list_policy],
        outputs = [make_address("write", pubkey[0]) for pubkey in list_policy],
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
