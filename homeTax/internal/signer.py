from pypinksign import PinkSign
from datetime import datetime
from base64 import b64encode

from cryptography.hazmat.primitives.serialization import Encoding


class Signer:
    def __init__(self, pinkSign: PinkSign) -> None:
        self.pinkSign = pinkSign

    def _get_serial(self):
        return hex(self.pinkSign.serialnum())[2:].rjust(8, "0")

    def _get_datetime_str(self):
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S")

    def sign_ssn(self, ssn: str) -> str:
        sig = self.pinkSign.sign(ssn.encode())

        res = [
            ssn,
            self._get_serial(),
            self._get_datetime_str(),
            b64encode(sig).decode(),
        ]

        return b64encode("$".join(res).encode()).decode()

    def get_pem(self) -> str:
        return self.pinkSign.pub_cert.public_bytes(Encoding.PEM).decode()

    def get_random_enc(self) -> str:
        return b64encode(bytes(self.pinkSign._rand_num.asNumbers())).decode()
