from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from urllib3 import request
from time import sleep
import json

my_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'

engine:Engine = create_engine(
    "sqlite:///rickandmorty.db", connect_args={"check_same_thread": False}
)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Voice_Actor(Base):
    __tablename__ = 'voice_actors'

    id = Column('id', Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    original_name = Column(String)
    gender = Column(Integer)
    adult = Column(Boolean)

    episode_character = relationship("EpisodeCharacterCast", back_populates="voice_actor")

    def __init__(self, id, name, original_name, gender, adult):
        self.id = id
        self.name = name
        self.original_name = original_name
        self.gender = gender
        self.adult = adult

class Character(Base):
    __tablename__='characters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    species = Column(String, index=True)
    s_type = Column(String, index=True)
    gender = Column(String)
    origin = Column(String)
    location = Column(String)
    image = Column(String)
    url = Column(String)

    episode_role = relationship("EpisodeCharacterCast", back_populates="character")

    def __init__(self, id, name, status, species, s_type, gender, origin, location, image, url):
        self.id = id
        self.name = name
        self.status = status
        self.species = species
        self.s_type = s_type
        self.gender = gender
        self.origin = origin
        self.location = location
        self.image = image
        self.url = url

    def __str__(self):
        return '%s - %i'%(self.name, self.id)

class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    episode_code = Column(String, unique=True)
    name = Column(String)
    air_date = Column(String)
    url = Column(String, unique=True)
    
    character_role = relationship("EpisodeCharacterCast", back_populates="episode")

    def __init__(self, id, episode_code, name, air_date, url):
        self.id = id
        self.episode_code = episode_code
        self.name = name
        self.air_date = air_date
        self.url = url
    
class EpisodeCharacterCast(Base):
    __tablename__ = 'EpisodeCharacterCasts'
    
    episode_id = Column(Integer, ForeignKey('episodes.id'), primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), primary_key=True)
    voice_actor_id = Column(Integer, ForeignKey('voice_actors.id'))

    episode = relationship("Episode", back_populates="character_role")
    character = relationship("Character", back_populates="episode_role")
    voice_actor = relationship("Voice_Actor", back_populates="episode_character")

    def __init__(self, ep_id, char_id, ep, char):
        self.episode_id = ep_id
        self.character_id = char_id

        self.episode = ep
        self.character = char
    
Base.metadata.create_all(bind=engine)

def collect(db:Session=session(), my_key:str=my_key) -> None:
    voice_actors:dict[int, Voice_Actor] = {}
    characters:dict[int, Character] = {}
    episodes:dict[int, Episode] = {}
    ep_char_cast:dict[str, EpisodeCharacterCast] = {}
    
    char_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/character').data)['info']['count'])
    chars_list:list[dict[str,str]] = json.loads(request('get', 'https://rickandmortyapi.com/api/character/%s'%(str(list(range(1, char_count+1))))).data)
    for char_dict in chars_list:
        characters[int(char_dict['id'])] = Character(
            int(char_dict['id']),
            char_dict['name'],
            char_dict['status'],
            char_dict['species'],
            char_dict['type'],
            char_dict['gender'],
            char_dict['origin']['name']+'_'+char_dict['origin']['url'],
            char_dict['location']['name']+'_'+char_dict['location']['url'],
            char_dict['image'],
            char_dict['url']
        )
    
    ep_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/episode').data)['info']['count'])
    for i in range(1, ep_count+1):
        episode_rem:dict[str, str] = json.loads(request('get', 'https://rickandmortyapi.com/api/episode/%i'%(i)).data)
        ep_id:int = int(episode_rem['id'])
        ep_episode:str = episode_rem['episode']
        ep_name:str = episode_rem['name']
        ep_url:str = episode_rem['url']

        print(ep_episode)
        
        episode_mvdb:dict[str, str] = json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/season/%i/episode/%i?api_key=%s&append_to_response=credits'%(int(ep_episode.split('E')[0][1:]), int(ep_episode.split('E')[1]), my_key)).data)
        ep_air_date:str = episode_mvdb['air_date']

        epi:Episode = Episode(
            ep_id,
            ep_episode,
            ep_name,
            ep_air_date,
            ep_url
        )

        ep_chars:list[Character] = [characters[int(c.rsplit('/', 1)[1])] for c in episode_rem['characters']]
        for ep_char in ep_chars:
            ep_char_cast['%i_%i'%(epi.id,ep_char.id)] = EpisodeCharacterCast(
                epi.id,
                ep_char.id,
                epi,
                ep_char
            )

        cast:list[dict[str, str]] = episode_mvdb['credits']['cast']+episode_mvdb['guest_stars']
        for vac in cast:
            if int(vac['id']) not in voice_actors:
                voice_actors[int(vac['id'])] = Voice_Actor(
                    int(vac['id']),
                    vac['name'],
                    vac['original_name'],
                    int(vac['gender']),
                    bool(vac['adult'])
                )
            va = voice_actors[int(vac['id'])]

            for char_name in vac['character'][:-8].split(' / '):
                for char in ep_chars:
                    if char_name != char.name:
                        continue

                    ep_char_cast['%i_%i'%(epi.id,char.id)].voice_actor_id = va.id

        episodes[ep_id] = epi
        sleep(0.25)
    
    db.add_all(voice_actors.values())
    db.add_all(characters.values())
    db.add_all(episodes.values())
    db.add_all(ep_char_cast.values())

    db.commit()

