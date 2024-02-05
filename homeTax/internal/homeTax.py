import re

from datetime import datetime
from pypinksign import PinkSign
from base64 import b64encode
from hashlib import sha256
import hmac

import xml.etree.ElementTree as elemTree
from cryptography.hazmat.primitives.serialization import Encoding

from .signer import Signer
from .http import new_http_session

hmac_keys = [
    b"bakfuRUXvh9c3POvkdfUDHF91jijBhV2BvsuWE966SY",
    b"rns6HuMkhT3FN8cIELHqYW51xHpk4oGOTetFjZ3Wog",
    b"ZobgiyO5GpHBj4XfBxpIsdtuxOVGOuxfvJ3cl7hg",
    b"tQpnppnLO4DhApYt4Wpi2fP3ikontfDj5e4gL8fatL0",
    b"qyDYuOUwZO2GCykWTJJZrgRIGTg6z3FPBrIAyHxxI",
    b"RF899ggdKY31TR3beawC7r7QbLAW1of4OrRaSWypA",
    b"ASNbDSqkpdq6ckOpIoGUyO5E6xeVulnMBIQJwOAvEI",
]
hmac_re = re.compile(r"[^0-9a-zA-Z]", re.IGNORECASE)


class HomeTax:
    def __init__(self, pinkSign: PinkSign):
        self._signer = Signer(pinkSign)

        self._user_id = ""
        self._session = new_http_session()

    def _make_hmac(self, data: str):
        now = datetime.now()
        sec = now.second

        key = hmac_keys[sec % len(hmac_keys)]

        hm = b64encode(
            hmac.digest(key, (data + self._user_id).encode(), sha256)
        ).decode()

        return hmac_re.sub("", hm)

    def _get_ssn(self):
        res = self._session.post(
            "https://www.hometax.go.kr/wqAction.do?actionId=ATXPPZXA001R01&screenId=UTXPPABA01",
            data=self._encode_data("<map></map>"),
        )

        tree = elemTree.fromstring(res.text)
        return tree.findtext("pkcEncSsn")

    def _encode_data(self, data: str):
        return data + "<nts<nts>nts>" + self._make_hmac(data)

    def new_session(self):
        self._user_id = ""
        self._session = new_http_session()

    def login(self):
        ssn = self._get_ssn()
        res = self._session.post(
            "https://www.hometax.go.kr/pubcLogin.do?domain=hometax.go.kr&mainSys=Y",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "logSgnt": self._signer.sign_ssn(ssn),
                "cert": self._signer.get_pem(),
                "randomEnc": self._signer.get_random_enc(),
                "pkcLoginYnImpv": "Y",
                "pkcLgnClCd": "03",
                "scrnId": "UTXPPABA01",
                # screen size
                "userScrnRslnXcCnt": "1680",
                "userScrnRslnYcCnt": "1050",
            },
        )

        return res.text

    def get_permissions(self):
        res = self._session.post(
            "https://hometax.go.kr/permission.do?screenId=index_pp",
            headers={"Content-Type": "application/xml"},
            data="<map id='postParam'><popupYn>false</popupYn></map>",
        )

        return res.text
