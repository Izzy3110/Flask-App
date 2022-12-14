import os
import sys
import base64
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

class SecMan(object):
    def __init__(self, privatekey_filedir, password_str):
        self.secret_code = password_str
        self.privatekey_filedir = privatekey_filedir
        self.privatekey_filename = "rsa_key.bin"
        self.privatekey_filepath = os.path.join(self.privatekey_filedir, self.privatekey_filename)
        
        self.pubkey_filename = self.privatekey_filename.rstrip(".bin") + ".pub"
        self.pubkey_filepath = os.path.join(privatekey_filedir, self.pubkey_filename)
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
        print(self.secret_code)
        
        
        private_key = RSA.import_key(
            open(self.privatekey_filepath, "rb").read(), 
            passphrase=self.secret_code
        )

        print(private_key)
        
        

        b_ = BytesIO()
        b_.write(base64.b64decode(input_base))
        b_.seek(0)

        
        
        enc_session_key, nonce, tag, ciphertext = [ b_.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
        return AES.new(PKCS1_OAEP.new(private_key).decrypt(enc_session_key), AES.MODE_EAX, nonce).decrypt_and_verify(ciphertext, tag).decode("utf-8")




def validate_post_data(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if not data.get('name') or not isinstance(data['name'], str):
        return False
    if data.get('age') and not isinstance(data['age'], int):
        return False
    return True
