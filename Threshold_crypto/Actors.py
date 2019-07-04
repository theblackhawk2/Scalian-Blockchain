from Crypto import Random
from Crypto.PublicKey import RSA
import base64

"""
Transaction Model :

{ 
  "from"  :"PubKey1"
  "To"    :"PubKey2"
  "Asset" :"Asset Id"
}
"""

KEY_LENGTH = 256*4

class Member:
    def __init__(self):
        self.pub_key  = ""
        self.priv_key = ""
        self.name     = ""
        self.generateKey()

    def generateKey(self):
        self.priv_key = RSA.generate(KEY_LENGTH, Random.new().read)
        self.pub_key  = self.priv_key.publickey()

    def encryptMessage(self,message,pub_key):
        encrypted = pub_key.encrypt(message.encode(), 32)[0]
        encoded_encrypted = base64.b64encode(encrypted)
        return encoded_encrypted
        
    def decryptMessage(self,enc_message):
        decoded_encrypted = base64.b64decode(enc_message)
        decoded_decrypted = self.priv_key.decrypt(decoded_encrypted)
        return decoded_decrypted.decode("utf-8")

class Writer(Member):
    def __init__(self):
        pass
    def generatePoly(self):
        pass
    def sendRequest(self):
        pass
    

class Reader(Member):
    def __init__(self):
        pass
    def requireAccess(self):
        pass

class AccessMember(Member):
    def __init__(self):
        pass

class SecretMember(Member):
    def __init__(self):
        pass


if __name__ == "__main__":
    """
    Test Assymetric Encryption Decryption [OK]
    M1 = Member()
    M2 = Member()
    enc = M1.encryptMessage("be encrypted by the public Key",M2.pub_key)
    dec = M2.decryptMessage(enc)
    print(dec)
    """
