# -*- coding: utf-8 -*-
"""
    __init__
    A library to get text to speech from micrsoft translation engine.
    See: https://www.microsoft.com/cognitive-services/en-us/speech-api/documentation/api-reference-rest/bingvoiceoutput
"""

try:
    import simplejson as json
except ImportError:
    import json
import logging

try:
    import httplib
except ImportError:
    import http.client as httplib


class BadRequestException(Exception):
    def __init__(self, message):
        self.message = str(message.status) + " " + str(message.reason)
        super(BadRequestException, self).__init__(self.message)
        
class AuthException(Exception):
    def __init__(self, message):
        self.message = str(message.status) + " " + str(message.reason)
        super(AuthException, self).__init__(self.message)
        
class LanguageException(Exception):
    def __init__(self, message):
        self.message = str(message)
        super(LanguageException, self).__init__(self.message)


class Translator(object):
    """
    Implements API for the Microsoft Translator service
    """
    auth_host = 'api.cognitive.microsoft.com'
    auth_path = '/sts/v1.0/issueToken'
    base_host = 'speech.platform.bing.com'
    base_path = ''
    def __init__(self, client_secret, debug=False):
        """
        :param clien_secret: The API key provided by Azure
        :param debug: If true, the logging level will be set to debug
        """
        self.client_secret = client_secret
        self.debug = debug
        self.logger = logging.getLogger("bingtts")
        self.access_token = None
        if self.debug:
            self.logger.setLevel(level=logging.DEBUG)
        
    def get_access_token(self):
        """
        Retrieve access token from Azure.
        
        :return: Text of the access token to be used with requests
        """
        headers={'Ocp-Apim-Subscription-Key' : self.client_secret}
        conn = httplib.HTTPSConnection(self.auth_host)
        conn.request(method="POST", url=self.auth_path, headers=headers, body="")
        response = conn.getresponse()    
        if int(response.status) != 200:
            raise AuthException(response)
        return response.read()
        
    def call(self, headerfields, path, body):
        """
        Calls Bing API and retrieved audio
        
        :param headerfields: Dictionary of all headers to be sent
        :param path: URL path to be appended to requests
        :param body: Content body to be posted
        """
        
        # If we don't have an access token, get one
        if not self.access_token:
            self.access_token = self.get_access_token()
        
        # Set authorization header to token we just retrieved
        try:
            headerfields["Authorization"] = "Bearer " + self.access_token
        except:
            headerfields["Authorization"] = "Bearer " + self.access_token.decode('utf-8')
        # Post to Bing API
        urlpath = "/".join([self.base_path, path])
        conn = httplib.HTTPSConnection(self.base_host)
        conn.request(method="POST", url=urlpath, headers=headerfields, body=body)
        resp = conn.getresponse()
        # If token was expired, get a new one and try again
        if int(resp.status) == 401:
            self.access_token = None
            return self.call(headerfields, path, body)
        
        # Bad data or problem, raise exception    
        if int(resp.status) != 200:
            raise BadRequestException(resp)
            
        return resp.read()
        
    def speak(self, text, lang, gender, format):
        """
        Gather parameters and call.
        
        :param text: Text to be sent to Bing TTS API to be
                     converted to speech
        :param lang: Language to be spoken
        :param gender: Gender of the speaker
        :param format: File format (see link below)
        
        Name maps and file format specifications can be found here:
        https://www.microsoft.com/cognitive-services/en-us/speech-api/documentation/api-reference-rest/bingvoiceoutput
        """
        
        namemap = {
            "ar-EG,Female" : "Microsoft Server Speech Text to Speech Voice (ar-EG, Hoda)",
            "de-DE,Female" : "Microsoft Server Speech Text to Speech Voice (de-DE, Hedda)",
            "de-DE,Male" : "Microsoft Server Speech Text to Speech Voice (de-DE, Stefan, Apollo)",
            "en-AU,Female" : "Microsoft Server Speech Text to Speech Voice (en-AU, Catherine)",
            "en-CA,Female" : "Microsoft Server Speech Text to Speech Voice (en-CA, Linda)",
            "en-GB,Female" : "Microsoft Server Speech Text to Speech Voice (en-GB, Susan, Apollo)",
            "en-GB,Male" : "Microsoft Server Speech Text to Speech Voice (en-GB, George, Apollo)",
            "en-IN,Male" : "Microsoft Server Speech Text to Speech Voice (en-IN, Ravi, Apollo)",
            "en-US,Male" : "Microsoft Server Speech Text to Speech Voice (en-US, BenjaminRUS)",
            "en-US,Female" : "Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)",
            "es-ES,Female" : "Microsoft Server Speech Text to Speech Voice (es-ES, Laura, Apollo)",
            "es-ES,Male" : "Microsoft Server Speech Text to Speech Voice (es-ES, Pablo, Apollo)",
            "es-MX,Male" : "Microsoft Server Speech Text to Speech Voice (es-MX, Raul, Apollo)",
            "fr-CA,Female" : "Microsoft Server Speech Text to Speech Voice (fr-CA, Caroline)",
            "fr-FR,Female" : "Microsoft Server Speech Text to Speech Voice (fr-FR, Julie, Apollo)",
            "fr-FR,Male" : "Microsoft Server Speech Text to Speech Voice (fr-FR, Paul, Apollo)",
            "it-IT,Male" : "Microsoft Server Speech Text to Speech Voice (it-IT, Cosimo, Apollo)",
            "ja-JP,Female" : "Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi, Apollo)",
            "ja-JP,Male" : "Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro, Apollo)",
            "pt-BR,Male" : "Microsoft Server Speech Text to Speech Voice (pt-BR, Daniel, Apollo)",
            "ru-RU,Female" : "Microsoft Server Speech Text to Speech Voice (ru-RU, Irina, Apollo)",
            "ru-RU,Male" : "Microsoft Server Speech Text to Speech Voice (ru-RU, Pavel, Apollo)",
            "zh-CN,Female" : "Microsoft Server Speech Text to Speech Voice (zh-CN, HuihuiRUS)",
            "zh-CN,Male" : "Microsoft Server Speech Text to Speech Voice (zh-CN, Kangkang, Apollo)",
            "zh-HK,Male" : "Microsoft Server Speech Text to Speech Voice (zh-HK, Danny, Apollo)",
            "zh-TW,Female" : "Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)",
            "zh-TW,Male" : "Microsoft Server Speech Text to Speech Voice (zh-TW, Zhiwei, Apollo)"
            }
        if not gender:
            gender = 'Female'
        if not lang:
            lang = 'en-US'
        if not format:
            format = 'riff-8khz-8bit-mono-mulaw'
        try:
            servicename = namemap[lang + ',' + gender]
        except (Exception):
            raise LanguageException("Invalid language/gender combination: %s, %s" % (lang, gender))
            
        headers = {
            "Content-type" : "application/ssml+xml",
            "X-Microsoft-OutputFormat" : format,
            "X-Search-AppId" : "07D3234E49CE426DAA29772419F436CA", 
            "X-Search-ClientID" : "1ECFAE91408841A480F00935DC390960", 
            "User-Agent" : "TTSForPython"
            }
            
        body = "<speak version='1.0' xml:lang='%s'><voice xml:lang='%s' xml:gender='%s' name='%s'>%s</voice></speak>" % (lang, lang, gender, servicename, text)
        
        return self.call(headers, "synthesize", body)
