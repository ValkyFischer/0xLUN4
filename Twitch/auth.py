import json
import http.server
import socketserver
import webbrowser
import requests

CODE = None


class NullOutput:
    def write(self, s):
        pass


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Suppress the default console output
        pass
    
    def do_GET(self):
        # Extract the OAuth code from the query parameters
        global CODE
        try:
            CODE = self.path.split('?code=')[1].split("&scope")[0]
        except IndexError:
            pass
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'OAuth code received. You can now close this page.')
        

class Auth:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        
    def authorize(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list):
        """
        Authorizes the bot to use the Twitch API.
        
        Args:
            client_id (str): The client id of the bot.
            client_secret (str): The client secret of the bot.
            redirect_uri (str): The redirect uri of the bot.
            scopes (list): The scopes of the bot.
        """
        self.logger.info('Authorizing Twitch Account')
        code = self._get_auth_code(client_id, redirect_uri, scopes)
        data = self._get_auth_token(client_id, client_secret, code, redirect_uri)
        
        self.config['twitch']['bot_token'] = data.get('access_token')
        self.config['twitch']['bot_refresh_token'] = data.get('refresh_token')
        self.config['twitch']['bot_token_expires'] = data.get('expires_in')
        
        return self.config['twitch']['bot_token']
        
    def _get_auth_code(self, client_id: str, redirect_uri: str, scopes: list) -> str:
        """
        Gets the OAuth code for the bot. This code will be used to get the OAuth token for the bot.
        
        Args:
            client_id (str): The client id of the bot.
            redirect_uri (str): The redirect uri of the bot.
            scopes (list): The scopes of the bot.
            
        Returns:
            str: The OAuth code for the bot.
        """
        url = f'https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={"+".join(scopes)}'
        # Create a local web server to listen for the response
        server_address = ('', 8000)  # You can choose a different port if needed
        httpd = socketserver.TCPServer(server_address, OAuthCallbackHandler)
        
        try:
            # Open the authorization URL in the browser for the user to log in and grant authorization
            webbrowser.open(url)
            # Start the web server to listen for the response
            httpd.handle_request()
        
        finally:
            # Close the web server when done
            httpd.server_close()

            if CODE is not None:
                self.logger.info(f'Twitch OAuth code received')
                return CODE
            else:
                raise Exception('Failed to get OAuth code')
        
    def _get_auth_token(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
        """
        Gets the OAuth token for the bot.
        
        Args:
            client_id (str): The client id of the bot.
            client_secret (str): The client secret of the bot.
            code (str): The OAuth code for the bot.
            redirect_uri (str): The redirect uri of the bot.
            
        Returns:
            str: The OAuth dict for the bot.
        """
        url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}'
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            self.logger.info(f'Twitch OAuth token received')
            return response_data
