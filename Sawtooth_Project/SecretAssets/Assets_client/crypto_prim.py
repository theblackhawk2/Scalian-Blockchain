# Elliptic Curves Library
from ecpy.curves           import Curve, Point
from ecpy.keys             import ECPublicKey, ECPrivateKey
from ecpy.eddsa            import EDDSA
from ecdsa.util            import randrange
from sympy.ntheory.factor_ import digits
from aes_encrypt           import *
from copy import copy

import hashlib
import os
import random


def lagrange(i,t):
    val = 1
    for j in range(1,t+2):
        if i == j:
            continue
        val *= j/float(j-i)
    return int(val)


def groupCouples(list):
    L = []
    if len(list)%2 != 0:
        print("Assurez vous que la liste est de longeur paire")
        return
    else:
        for i in range(len(list)//2):
            L.append([list[2*i],list[2*i+1]])
    return L

def convertToDecimal(coords,base):
    L = copy(coords)
    L.reverse()
    V = 0
    for i in range(len(L)):
        V += L[i]*(base**i)
    return V 

def ascii(text):
    l = [ord(i) for i in text]
    return l
    
class PVSS:
    def __init__(self,id,prime= "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"):
        self.id         = id
        self.pubKey     = ""
        self.privKey    = ""
        self.poly       = []
        self.curve      = Curve.get_curve("secp256k1")
        self.prime      = int(prime,16)
    def generateKey(self):
        seed         = hashlib.sha256(os.urandom(87)).hexdigest()
        self.privKey = ECPrivateKey(int(seed,base=16),self.curve)
        self.pubKey  = self.privKey.get_public_key()

    def generatePoly(self,t,prime = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"):
        for i in range(t):
            self.poly.append(random.randint(10000,int(prime,16)))


    def polyVal(self,x):
        Value = 0
        for i in range(len(self.poly)):
            Value += (x**i)*self.poly[i]
        return Value

    def showInfos(self):
        print("Member : {} has Public Key :{}".format(self.id,self.pubKey))
    
    
    def encrypt(self,text,pubKey):
        """
        Nous supposons que les informations 'G : point generateur'
        et ' AES : Methode de chiffrement ' sont connus publiquement
        """
        # Generate random AES key
        seed       = hashlib.sha256(os.urandom(87)).hexdigest()
        k          = int(seed,base=16)
        R          = k*self.curve.generator
        S          = k*pubKey.W
        AESKey     = S.x.to_bytes(32,byteorder="big")
        cipher = AESCipher(AESKey)
        encrypted = cipher.encrypt(text)
        # Le chiffrement est la donnée 
        return [R,encrypted]
    
    @staticmethod
    def decrypt(self,R,encrypted):
        S          = self.privKey.d * R
        AESKey     = S.x.to_bytes(32,byteorder="big")
        cipher     = AESCipher(AESKey)
        decrypted  = cipher.decrypt(encrypted)
        return decrypted

    @staticmethod
    def symetric_encrypt(text,key):
        AESKey    = int(key).to_bytes(32,byteorder="big")
        cipher    = AESCipher(AESKey)
        encrypted = cipher.encrypt(text)
        return encrypted

    @staticmethod
    def symetric_decrypt(encrypted,key):
        AESKey    = int(key).to_bytes(32,byteorder="big")
        cipher    = AESCipher(AESKey)
        decrypted = cipher.decrypt(encrypted)
        return decrypted
    
    
    def secret_split(self,secret, t, n,h):

        O = self.prime
        
        assert(n >= t)

        coef = [secret] + [randrange(O) for i in range(1, t)]

        f = lambda x: sum([ coef[i] * pow(x, i) for i in range(t)]) % O

        secret_share = list(map(f, list(range(1, n + 1))))

        F = [ coef[j] * h for j in range(t) ]
         
        return (secret_share, F) 
    
    @staticmethod
    def verify_secret_share(self,secret_share, i, F,G):

        #G = self.curve.generator
        
        verify = F[0]

        for j in range(1, len(F)):
            verify += pow(i+1, j) * F[j]

        return verify == secret_share * G
    
    
    @staticmethod
    def reconstruct_key(self,sub_secret_share, t):

        O = self.prime
        assert(len(sub_secret_share) >= t)
        recon_key = 0
        
        for j in range(1, t + 1):
            mult = 1
            
            for h in range(1, t + 1):
                if h != j:
                    mult *= ( h / (h - j))

            recon_key += (sub_secret_share[j - 1] * int(mult)) % O

        return recon_key % O

    @staticmethod
    def encryptShare(share,pubKey):
        return share*pubKey

    @staticmethod
    def decryptShare(self,share):
        return pow(self.privKey.d,self.prime - 2,self.prime)
