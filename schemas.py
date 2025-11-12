from typing import Optional
import database

# ------------------ Base Schemas (Dados Brutos) ------------------
class myEpisode():
    id:int
    episode_code:str
    name:str
    air_date:str
    url:str

    cast:list[tuple['myCharacter', 'myVoiceActor']]

    def __init__(self, ep:database.Episode, cast:list[tuple['myCharacter', 'myVoiceActor']] = []):
        self.id = ep.id
        self.episode_code = ep.episode_code
        self.name = ep.name
        self.air_date = ep.air_date
        self.url = ep.url

        if cast:
            self.cast = cast

class myCharacter():
    id:int
    name:str
    status:str
    species:str
    s_type:str
    gender:str
    origin:str
    location:str
    image:str
    url:str

    played_by:Optional[list['myVoiceActor']]
    episodes_in:Optional[list[tuple[myEpisode, 'myCharacter']]]

    def __init__(self, char:database.Character):
        self.id = char.id
        self.name = char.name
        self.status = char.status
        self.species = char.species
        self.s_type = char.s_type
        self.gender = char.gender
        self.origin = char.origin
        self.location = char.location
        self.image = char.image
        self.url = char.url

class myVoiceActor():
    id:int
    name:str
    original_name:str
    gender:str
    adult:str

    characters:list[myCharacter]
    episodes:list[myEpisode]
    episodes_role:list[tuple[myEpisode, myCharacter]]

    def __init__(self, va:database.Voice_Actor, chars:list[myCharacter] = [], episodes:list[myEpisode] = [], episodes_role:list[tuple[myEpisode, myCharacter]] = []):
        self.id = va.id
        self.name = va.name
        self.original_name = va.original_name
        self.gender = va.gender
        self.adult = va.adult

        if chars:
            self.characters = chars
        if episodes:
            self.episodes_in = episodes
        if episodes_role:
            self.episodes_role = episodes_role