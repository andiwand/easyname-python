import http.client as httpclient
import hashlib
import base64
import json
import collections
import time

class EasynameApi:
    HOST = "api.selenium.eu"
    PORT = httpclient.HTTPS_PORT
    
    __API_KEY_HEADER = "X-User-ApiKey"
    __AUTHENTICATION_HEADER = "X-User-Authentication"
    __DEFAULT_HEADER = {"Accept": "application/json"}
    
    #http status codes: https://devblog.selenium.eu/api/request-response/
    #api status codes: https://devblog.selenium.eu/wp-content/uploads/2012/09/api-statuscodes-errorcodes.pdf
    
    @staticmethod
    def _value_string(value):
        if isinstance(value, bool): return "1" if value else ""
        return str(value)
    
    def __init__(self, user_id, email, api_key, authentication_salt, signature_salt):
        self.__connection = httpclient.HTTPSConnection(EasynameApi.HOST, EasynameApi.PORT)
        self.__user_id = user_id
        self.__email = email
        self.__api_key = api_key
        self.__authentication_salt = authentication_salt
        self.__signature_salt = signature_salt
        self.__authentication = self._calculate_authentication()
    
    def _calculate_authentication(self):
        auth_raw = self.__authentication_salt % (self.__user_id, self.__email)
        auth_md5_hex = hashlib.md5(auth_raw).hexdigest()
        auth = base64.b64encode(auth_md5_hex)
        return auth
    
    def _calculate_signature(self, data, timestamp):
        od = collections.OrderedDict(sorted(data.items() + [("timestamp", timestamp), ]))
        values = "".join((EasynameApi._value_string(value) for value in od.values()))
        center = len(values) - len(values) / 2
        signature_raw = values[0:center] + self.__signature_salt + values[center:]
        signature_md5_hex = hashlib.md5(signature_raw).hexdigest()
        signature = base64.b64encode(signature_md5_hex)
        return signature
    
    def request(self, method, path, data=None, timestamp=None):
        if timestamp == None: timestamp = int(time.time())
        
        headers = dict(EasynameApi.__DEFAULT_HEADER)
        headers[EasynameApi.__API_KEY_HEADER] = self.__api_key
        headers[EasynameApi.__AUTHENTICATION_HEADER] = self.__authentication
        
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
