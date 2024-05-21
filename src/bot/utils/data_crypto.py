import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCrypther(object):
    def __init__(self, key: str):
        self.block_size = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data) -> bytes:
        """
        Кодирование данных

        :param data: данные для шифрования
        """
        raw = self._padlock(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Декодирование данных

        :param encrypted_data: Bytes строка для декодирования
        """
        enc = base64.b64decode(encrypted_data)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _padlock(self, data):
        return data + (self.block_size - len(data) % self.block_size) * \
            chr(self.block_size - len(data) % self.block_size)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
