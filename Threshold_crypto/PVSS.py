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

class OCS:
    def __init__(self):
        self.writer = []
        self.reader = []
        self.transaction = []
        self.smc = []

    def writeTransaction(self):
        pass
    def readTransaction(self):
        pass
    def testConsistency(self):
        pass
    def initActors(self):
        pass
    
class Member:
    def __init__(self,id,prime= 2**252 + 27742317777372353535851937790883648493):
        self.id         = id
        self.pubKey     = ""
        self.privKey    = ""
        self.poly       = []
        self.curve      = Curve.get_curve("Ed25519")
        self.prime      = prime
    def generateKey(self):
        seed         = hashlib.sha256(os.urandom(87)).hexdigest()
        self.privKey = ECPrivateKey(int(seed,base=16),self.curve)
        self.pubKey  = self.privKey.get_public_key()

    def generatePoly(self,t,prime = 2**252 + 27742317777372353535851937790883648493):
        for i in range(t):
            self.poly.append(random.randint(10000,prime))


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

    def decrypt(self,R,encrypted):
        S          = self.privKey.d * R
        AESKey     = S.x.to_bytes(32,byteorder="big")
        cipher     = AESCipher(AESKey)
        decrypted  = cipher.decrypt(encrypted)
        return decrypted
    
    def secret_split(self,secret, t, n,G):
        #G = self.curve.generator
        
        O = self.prime
        
        assert(n >= t)

        coef = [secret] + [randrange(O) for i in range(1, t)]

        f = lambda x: sum([ coef[i] * pow(x, i) for i in range(t)]) % O

        secret_share = list(map(f, list(range(1, n + 1))))

        F = [ coef[j] * G for j in range(t) ]
         
        return (secret_share, F) 

    def verify_secret_share(self,secret_share, i, F,G):

        #G = self.curve.generator
        
        verify = F[0]

        for j in range(1, len(F)):
            verify += pow(i+1, j) * F[j]

        return verify == secret_share * G

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

    def encryptShare(self,share,pubKey):
        return share*pubKey


    def decryptShare(self,share):
        return pow(self.privKey.d,self.prime - 2,self.prime)



if __name__ == "__main__":
    
    """
    Random Basepoint generation.
    seed     = hashlib.sha256(os.urandom(87)).hexdigest()
    crv      = Curve.get_curve("Ed25519")
    pvKey    = ECPrivateKey(int(seed,base=16),crv)
    print(pvKey)
    pbKey    = pvKey.get_public_key()
    """
    

    # OCS Protocol
    W = Member("Writer")
    R = Member("Reader")
    W.generateKey()
    R.generateKey()

    G = W.curve.generator

    secretAuthority = []
    for i in range(10): 
        A = Member("A"+str(i+1))
        A.generateKey()
        secretAuthority.append(A)

    # Random Basepoint generation 
    seed     = hashlib.sha256(os.urandom(87)).hexdigest()
    h        = ECPrivateKey(int(seed,base=16),W.curve).get_public_key().W
    
    Transaction = {
        "policy" : [],
        "secret" : 0,
        "encryptedShares" : [],
        "nizkProofs"      : [],
        "polyCommitments" : [],
        "encMessage"      : "",
        "Hc"              : ""
    }

    # Transaction["policy"].append(pointEncode(R.pubKey))
    """
    W.generatePoly(7)
    
    s = W.polyVal(0)

    Reconst = lagrange(1,7)*W.polyVal(1)
    for i in range(2,9):
        Reconst += lagrange(i,7)*W.polyVal(i)

    print("Secret : " + str(s))
    print("Reconstructed : "+str(Reconst))

    Secret = s*G
    

    polyComs = []
    for i in range(7):
        polyComs.append(W.poly[i] * h)

    for i in range(len(secretAuthority)):
        secretAuthority[i].share = W.polyVal(i+1)*secretAuthority[i].pubKey.W
       
        privKey = secretAuthority[i].privKey.d
        secretAuthority[i].directShare = W.polyVal(i+1)*W.curve.generator
        secretAuthority[i].decShare = pow(privKey,W.prime - 2,W.prime)*secretAuthority[i].share

 
    Reconstructed = lagrange(1,7)*secretAuthority[0].decShare
    
    for i in range(2,9):
        Reconstructed += lagrange(i,7)*secretAuthority[i-1].decShare

    print("Secret = "+str(Secret.x))
    print("Reconstructed = "+str(Reconstructed.x))
    """


    # for i in range(len(secretAuthority)):
    # Lagrange interpolation test

    Shares, Commitments = W.secret_split(111222333,9,20,h)
    print("Shares before encryption")
    print("\n")
    for i in range(len(Shares)):
        print("Share No "+str(i)+" : "+str(Shares[i]))
    
    print("\n")
    #print(Shares)
    #print(Commitments)
    decryptedShares = []
    for i in range(1,10):
        encShare = W.encrypt(str(Shares[i]),secretAuthority[i].pubKey)
        print("Encrypted Share No "+str(i)+" : "+str(encShare[1]))
        decShare = secretAuthority[i].decrypt(encShare[0],encShare[1])
        decryptedShares.append(int(decShare))
    print("\n")

    print("The result after Encryption / decryption : \n")

    for i in range(len(decryptedShares)):
        verify = W.verify_secret_share(decryptedShares[i],i+1,Commitments,h)
        print("Share No "+str(i+1)+" : "+str(decryptedShares[i])+" and the verification result is : "+str(verify))
    
    print("\n")
    
    key = W.reconstruct_key(decryptedShares,9)

    print("Reconstructed Key : "+str(key))