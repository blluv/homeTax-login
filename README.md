# 홈택스 공인인증서 로그인

```py
import pypinksign
from getpass import getpass
from homeTax import HomeTax

p = pypinksign.PinkSign()
p.load_pubkey(pubkey_path="./signCert.der")
p.load_prikey(prikey_path="./signPri.key", prikey_password=getpass().encode())

homeTax = HomeTax(p)
print(homeTax.login())
print(homeTax.get_permissions())
```
