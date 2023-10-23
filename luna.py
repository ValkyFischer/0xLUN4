import json

import requests


class Luna:
    
    def __init__(self, logger, config):
        self.config = config
        self.logger = logger
        
        self.luna_origin = f'https://{self.config["luna"]["host"]}:{self.config["luna"]["port"]}'
        self.luna_version = f'v{self.config["luna"]["version"]}'
        self.luna_rest_url = f'{self.luna_origin}/rest/{self.luna_version}'
        
        self.response = {"msg": "API Error!", "Return": False, "ReturnCode": 3}
    
    def _pingUrl(self) -> str:
        return f'{self.luna_rest_url}/ping'
    
    def _translateUrl(self) -> str:
        return f'{self.luna_rest_url}/translate'
    
    def _askUrl(self) -> str:
        return f'{self.luna_rest_url}/ask'
    
    def lunaPing(self) -> dict:
        response = self.response
        
        try:
            x = requests.post(url=self._pingUrl(), json={})
            ping = int(x.elapsed.microseconds / 1000)
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": ping
            }
            self.logger.info(f'Luna Ping | Latency: {ping}ms')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
    
    async def lunaTranslate(self, text: str, lang: str = "en") -> dict:
        response = self.response
        request_data = {
            "message": text,
            "language": lang
        }
        headers = {"Content-Type": "application/json"}
        self.logger.info(f'Luna Translate | Text: {text}')
        try:
            x = requests.request(method="POST", url=self._translateUrl(), json=request_data, headers=headers)
            data = x.json()
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": data['Data']
            }
            self.logger.info(f'Luna Translate | Answer: {data}')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
    
    async def lunaAsk(self, text: str) -> dict:
        response = self.response
        request_data = {
            "message": text
        }
        headers = {"Content-Type": "application/json"}
        try:
            x = requests.request(method="POST", url=self._askUrl(), json=request_data, headers=headers)
            data = x.json()
            
            response = {
                "msg": "Command successfull",
                "Return": True,
                "ReturnCode": 1,
                "data": data['Data']
            }
            self.logger.info(f'Luna Ask | Question: {text}')
            self.logger.info(f'Luna Ask | Answer: {data}')
            
        except requests.RequestException as e:
            self.logger.error(f'Failed to make the request: {str(e)}')
        
        return response
