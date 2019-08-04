import sys
import getopt
import urllib.request
import hashlib
import json
from hashlib import sha512
from urllib.error import HTTPError

from ecpy.curves           import Curve, Point
from ecpy.keys             import ECPublicKey, ECPrivateKey
from ecpy.eddsa            import EDDSA
from ecdsa.util            import randrange
from sympy.ntheory.factor_ import digits
from crypto_prim           import *


# Script for generating mock secret authority

P = PVSS(0)
file = open("secretAuth.txt", "w")
for i in range(5):
    Pvkey = randrange(P.prime)
    pubKey = Pvkey*P.curve.generator
    file.write(str(pubKey.x)+','+str(pubKey.y)+','+str(Pvkey)+"\n")
file.close()
