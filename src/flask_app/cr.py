import os
import sys
import base64
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP



class SecMan(object):
    def __init__(self, privatekey_filepath, password_str):
        self.secret_code = password_str
        self.privatekey_filepath = privatekey_filepath
        self.pubkey_filename = os.path.basename(privatekey_filepath).rstrip(".bin") + ".pub"
        self.pubkey_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.pubkey_filename)
        super(SecMan, self).__init__()
        
    def encrypt_to_base(self, data: bytes) -> str:
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)

        b_ = BytesIO()
        b_.seek(0)
        [ b_.write(x) for x in (PKCS1_OAEP.new(RSA.import_key(open(self.pubkey_filepath).read())).encrypt(session_key), cipher_aes.nonce, tag, ciphertext) ]
        
        return base64.b64encode(b_.getvalue()).decode("utf-8")
        

    def decrypt_from_base(self, input_base) -> str:
        private_key = RSA.import_key(
            open(self.privatekey_filepath, "rb").read(), 
            passphrase=self.secret_code
        )

        b_ = BytesIO()
        b_.write(base64.b64decode(input_base))
        b_.seek(0)

        enc_session_key, nonce, tag, ciphertext = [ b_.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
        return AES.new(PKCS1_OAEP.new(private_key).decrypt(enc_session_key), AES.MODE_EAX, nonce).decrypt_and_verify(ciphertext, tag).decode("utf-8")

secret_code = "UnguessablePW123!"
secman = SecMan("rsa_key.bin", secret_code)

print(secman.decrypt_from_base(secman.encrypt_to_base("test".encode("utf-8"))))
