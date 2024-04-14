import typing


class MessageWithMedia:
    text: str
    media: typing.Union[typing.List, None]

    def __init__(self, text, media):
        self.text = text
        self.media = media

