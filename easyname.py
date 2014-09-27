import httplib
import md5
import base64
import binascii
import json
import collections
import time


class easyname:
    HOST = "api.easyname.eu"
    PORT = httplib.HTTPS_PORT
    
    __API_KEY_HEADER = "X-User-ApiKey"
    __AUTHENTICATION_HEADER = "X-User-Authentication"
    __DEFAULT_HEADER = {"Accept": "application/json"}
    
    #http status codes: https://devblog.easyname.eu/api/request-response/
    #api status codes: https://devblog.easyname.eu/wp-content/uploads/2012/09/api-statuscodes-errorcodes.pdf
    
    @staticmethod
    def _value_string(value):
        if isinstance(value, bool): return "1" if value else ""
        return str(value)
    
    def __init__(self, user_id, email, api_key, authentication_salt, signature_salt):
        self.__connection = httplib.HTTPSConnection(easyname.HOST, easyname.PORT)
        self.__user_id = user_id
        self.__email = email
        self.__api_key = api_key
        self.__authentication_salt = authentication_salt
        self.__signature_salt = signature_salt
        self.__authentication = self._calculate_authentication()
    
    def _calculate_authentication(self):
        auth_raw = self.__authentication_salt % (self.__user_id, self.__email)
        auth_md5 = md5.new(auth_raw).digest()
        auth_md5_hex = binascii.hexlify(auth_md5)
        auth = base64.b64encode(auth_md5_hex)
        return auth
    
    def _calculate_signature(self, data, timestamp):
        od = collections.OrderedDict(sorted(data.items() + [("timestamp", timestamp), ]))
        values = "".join((easyname._value_string(value) for value in od.values()))
        center = len(values) - len(values) / 2
        signature_raw = values[0:center] + self.__signature_salt + values[center:]
        signature_md5 = md5.new(signature_raw).digest()
        signature_md5_hex = binascii.hexlify(signature_md5)
        signature = base64.b64encode(signature_md5_hex)
        return signature
    
    def request(self, method, path, data=None, timestamp=None):
        if timestamp == None: timestamp = int(time.time())
        
        headers = dict(easyname.__DEFAULT_HEADER)
        headers[easyname.__API_KEY_HEADER] = self.__api_key
        headers[easyname.__AUTHENTICATION_HEADER] = self.__authentication
        
        body = None
        if data != None:
            signature = self._calculate_signature(data, timestamp)
            body = {"data": data, "timestamp": timestamp, "signature": signature}
            body = json.dumps(body, separators=(',',':'))
        
        self.__connection.request(method, path, body, headers)
        response = self.__connection.getresponse()
        rasponse_body = json.load(response)
        #TODO: check signature
        
        return rasponse_body, response.status, response.reason


e = easyname(39249, "stefl.andreas@gmail.com", "nK19XEqSXOx2oU", "d31nt13%se8cu9x3%sJBy3od", "J4H9Uz990usSi3gL2d")

r = e.request("GET", "/domain")[0]
domain_id = r["data"][0]["id"]

print e.request("GET", "/domain/%s" % domain_id)
print e.request("GET", "/domain/%s/dns" % domain_id)

data = {"name": "test", "type": "TXT", "content": "hallo welt", "ttl": 300}
print e.request("POST", "/domain/%s/dns" % domain_id, data)
