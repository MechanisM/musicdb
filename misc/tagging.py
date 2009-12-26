
from mutagen import File, mp3, easyid3


data = {
    'title': 'String Quartet in B-flat (Fitzwilliam Quartet)',
    'artist': 'Mozart',
    'tracknumber': '1',
    'genre': 'Classical',
    'date': '1997',
}

def tag(filename, data):
    audio = File(filename)
    audio.delete()
    if isinstance(audio, mp3.MP3):
        audio.tags = easyid3.EasyID3()
    audio.update(data)
    audio.save()

tag('01.flac', data)
tag('01.mp3', data)
