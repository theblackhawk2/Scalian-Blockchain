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


# First public Key

context = create_context('secp256k1')
private_key = Secp256k1PrivateKey.from_hex('853c35fae67d072f6edab47612ce453e0af1b87c9bfc46b6f1108c6a7b61170d')
signer      = CryptoFactory(context).new_signer(private_key)

public1     = signer.get_public_key().as_hex()

print(public1)
cv      = Curve.get_curve("secp256k1") 
public2 = ECPrivateKey(int('853c35fae67d072f6edab47612ce453e0af1b87c9bfc46b6f1108c6a7b61170d',16),cv).get_public_key()

print(public2)


policy = json.dumps({'members' : ['853c35fae67d072f6edab47612ce453e0af1b87c9bfc46b6f1108c6a7b61170d','853c35fae67d072f6edab47612ce453e0af1b87c9bfc46b6f1108c6a7b614444'] })
print(policy.encode('utf-8'))
seed = hashlib.sha256(policy.encode()).hexdigest()
a = (int(seed,16)*cv.generator).__str__()

print(a)
