import httplib
import md5
import base64
import binascii
import json
import collections
from datetime import datetime
import sys


def value_string(value):
    if isinstance(value, bool): return "1" if value else ""
    return str(value)

def calculate_signature(signature_salt, data, timestamp=None):
    if timestamp == None: timestamp = datetime.utcnow()
    
    od = collections.OrderedDict(sorted(data.items() + [("timestamp", timestamp), ]))
    values = "".join((value_string(value) for value in od.values()))
    center = len(values) - len(values) / 2
    signature_raw = values[0:center] + signature_salt + values[center:]
    signature_md5 = md5.new(signature_raw).digest()
    signature_md5_hex = binascii.hexlify(signature_md5)
    
    signature = base64.b64encode(signature_md5_hex)
    return signature

print calculate_signature("SuperSecretSigningSalt", {
      "id": 1234,
      "domain": "example.com",
      "expire": "2015-03-05",
      "trustee": False,
      "purchased": "2010-03-05"
  }, 1234567890)

sys.exit()


HOST = "api.easyname.com"
PORT = 443

USER_ID = 39249
EMAIL = "stefl.andreas@gmail.com"
KEY = "nK19XEqSXOx2oU"
AUTH_SALT = "d31nt13%se8cu9x3%sJBy3od"
SIGN_SALT = "J4H9Uz990usSi3gL2d"

AUTH_RAW = AUTH_SALT % (USER_ID, EMAIL)
AUTH_MD5 = md5.new(AUTH_RAW).digest()
AUTH_MD5_HEX = binascii.hexlify(AUTH_MD5)
AUTH = base64.b64encode(AUTH_MD5_HEX)

KEY_HEADER = "X-User-ApiKey"
AUTH_HEADER = "X-User-Authentication"

c = httplib.HTTPSConnection(HOST, PORT)

headers = {KEY_HEADER: KEY, AUTH_HEADER: AUTH, "Accept": "application/json"}

c.request("GET", "/domain", headers=headers)
r = c.getresponse()

print r.read()