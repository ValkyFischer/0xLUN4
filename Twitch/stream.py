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
