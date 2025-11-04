from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from urllib3 import request
import json

themoviedb_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'

engine = create_engine(
    "sqlite:///voice_actors.db", connect_args={"check_same_thread": False} # Necessário para SQLite com FastAPI
)

# SessionLocal: cria sessões individuais para cada requisição
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base: a classe base para criar os modelos de dados
Base = declarative_base()

""" # Dependência para obter a sessão do DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 """

class Voice_Actor(Base):
    __tablename__ = 'voice_actors'

    id = Column('id', Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)
    url = Column(String) 
    characters = relationship("Character", back_populates="voice_actors")

    def __init__(self, name, url, characters):
        self.name = name
        self.url = url
        self.characters = characters

# 3. Modelo Character (Personagem)
# Detalhes do personagem dublado
class Character(Base):
    __tablename__='characters'

    # Dados da API Rick and Morty
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    species = Column(String, index=True) # Importante para o requisito de filtro
    s_type = Column(String, index=True) # Importante para o requisito de filtro
    gender = Column(String)
    origin = Column(String)
    location = Column(String)
    image = Column(String)
    
    # Chave Estrangeira: Aponta para o Actor que dubla este personagem
    actor_id = Column(Integer, ForeignKey("voice_actors.id"))
    
    # Relação Muitos-para-1: Vários personagens são dublados pelo mesmo ator
    actor = relationship("Actor", back_populates="characters")
    
    # Relação Muitos-para-Muitos: Personagens <-> Episódios
    episodes = relationship(
        "Episode",
        secondary='character_episode_association',
        back_populates="characters"
    )

# 4. Modelo Episode (Episódio da Série)
# Informações sobre os episódios em que um dublador (Actor) atuou
class Episode(Base):
    __tablename__ = "episodes"

    # Dados da API Rick and Morty
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    air_date = Column(String)
    episode_code = Column(String, unique=True) # Ex: S01E01
    
    # Dados da integração com TMDB (Metadados da série/episódio)
    tmdb_rating = Column(String, nullable=True)
    tmdb_overview = Column(Text, nullable=True) # Text para conteúdo mais longo
    
    # Relação Muitos-para-Muitos: Episódios <-> Personagens
    characters = relationship(
        "Character",
        secondary='character_episode_association',
        back_populates="episodes"
    )

Base.metadata.create_all(bind=engine)

voice_actor_dict:dict[str, list[str]] = {}
for voice_actor in json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key=%s'%(my_key)).data)['cast']:
    chars:list[str] = []
    
    for r in voice_actor['roles']:
        for name in r['character'].split(' / '):
            if name.endswith('(voice)'):
                name = name.split('(')[0][:-1]
            if name == '' or name =='Additional Voices':
                continue
            chars.append(name)

    if not chars:
        continue

    voice_actor_dict[voice_actor['name']] = chars

""" print(*voice_actor_dict.items(), sep='\n')
print(sum([len(v) for v in voice_actor_dict.values()])) """

characters_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/character').data)['info']['count'])
for c in json.loads(request('get', 'https://rickandmortyapi.com/api/character/%s'%(','.join([str(i) for i in range(1, characters_count+1)]))).data)[234:235]:
    print(c)