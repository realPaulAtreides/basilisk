from jsonrpcclient.clients.http_client import HTTPClient
from jsonrpcclient.requests import Request
import ecdsa
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class WalletOwnerV3Proxy:
    def __init__(self, endpoint, api_secret_file):
        self.client = HTTPClient(endpoint)
        with open(api_secret_file) as file:
            self.api_password = file.read().strip()
        self.api_user = 'grin'
        self.client.session.auth = (self.api_user, self.api_password)
        self.ecdh = WalletOwnerV3Proxy._create_key()
        self.shared_key = self.init_secure_api()

    @staticmethod
    def _create_key():
        ecdh = ecdsa.ECDH(curve=ecdsa.SECP256k1)
        ecdh.generate_private_key()
        return ecdh

    def decrypt_response(self, response):
        encrypted_body = b64decode(response.data.result['Ok']['body_enc'])
        nonce = bytes.fromhex(response.data.result['Ok']['nonce'])
        decipher = AES.new(self.shared_key, AES.MODE_GCM, nonce=nonce)
        enc_text = encrypted_body[:-16]
        tag = encrypted_body[-16:]
        decrypted_response = decipher.decrypt_and_verify(enc_text, tag)
        response = json.loads(decrypted_response.decode("utf-8"))

        if 'error' in response:
            raise Exception(response['error']['message'])


        return response

    def send_enc(self, payload):
        enc_payload, nonce = self.make_enc_payload(payload)
        response = self.client.send(
            Request(
                'encrypted_request_v3',
                nonce=nonce.hex(),
                body_enc=enc_payload
            )
        )
        if not response.data.ok:
            raise Exception(response.message)
        return self.decrypt_response(response)

    def make_enc_payload(self, payload):
        nonce = get_random_bytes(12)
        cipher = AES.new(self.shared_key, AES.MODE_GCM, nonce=nonce)
        cipher_text, tag = cipher.encrypt_and_digest(bytes(json.dumps(payload), 'utf-8'))
        encrypted_payload = cipher_text + tag
        return b64encode(encrypted_payload).decode('utf-8'), nonce

    def init_secure_api(self):
        response = self.client.send(
            Request(
                "init_secure_api",
                ecdh_pubkey=self.ecdh.get_public_key().to_string('compressed').hex()
            )
        )
        if not response.data.ok:
            raise Exception(response.message)

        self.ecdh.load_received_public_key_bytes(bytes.fromhex(response.data.result["Ok"]))
        return self.ecdh.generate_sharedsecret_bytes()

    def open_wallet(self, _name, _password):
        if _password[-7:] == '.secret':
            with open(_password, 'r') as file:
                _password = file.read().replace('\n', '')
        payload = Request('open_wallet', name=_name, password=_password)
        response = self.send_enc(payload)
        self.token = response['result']['Ok']

    def _call(self, method_name, *args, **kwargs):
        for arg in args:
            kwargs.update(arg)
        kwargs.update({'token': self.token})
        response = self.send_enc(Request(method_name, **kwargs))
        return response

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        f = lambda *args, **kwargs: self._call(name, *args, **kwargs)
        f.__name__ = name
        return f

