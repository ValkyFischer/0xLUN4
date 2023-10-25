import aiohttp


class Stream:
    """
    A class storing Twitch stream information.
    
    Properties:
        - title (str): The title of the stream.
        - game (Game): The game being played on the stream.
        - tags (list): The tags of the stream.
        - language (str): The language of the stream.
        - classification (list): The classification of the stream.
    """
    def __init__(self):
        self.title = ''
        self.game = Game()
        self.tags = []
        self.language = ''
        self.classification = []

class Game:
    """
    A class storing Twitch stream game information.
    
    Properties:
        - name (str): The name of the game.
        - id (int): The id of the game.
    """
    def __init__(self):
        self.name = ''
        self.id = 0
    
    async def get_id(self, name: str, client_id: str, bot_token: str) -> int:
        """
        Gets the game id from the game name.
        
        Args:
            name (str): The name of the game.
            client_id (str): The client id of the bot.
            bot_token (str): The OAuth token of the bot.
            
        Returns:
            int: The id of the game.
        """
        url = f'https://api.twitch.tv/helix/games?name={name}'
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {bot_token}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data['data'][0]['id']
