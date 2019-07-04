from Crypto import Random
from Crypto.PublicKey import RSA
import base64

def generate_keys():
   # key length must be a multiple of 256 and >= 1024
   modulus_length = 256*4
   privatekey = RSA.generate(modulus_length, Random.new().read)
   publickey = privatekey.publickey()
   return privatekey, publickey

def encrypt_message(a_message , publickey):
   encrypted_msg = publickey.encrypt(a_message, 32)[0]
   encoded_encrypted_msg = base64.b64encode(encrypted_msg)
   return encoded_encrypted_msg

def decrypt_message(encoded_encrypted_msg, privatekey):
   decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
   decoded_decrypted_msg = privatekey.decrypt(decoded_encrypted_msg)
   return decoded_decrypted_msg

a_message = "This is the illustration of RSA algorithm of asymmetric cryptography"
privatekey , publickey = generate_keys()
encrypted_msg = encrypt_message(a_message , publickey)
decrypted_msg = decrypt_message(encrypted_msg, privatekey)


