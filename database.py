from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from urllib3 import request
import json

themoviedb_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'

engine = create_engine(
    "sqlite:///voice_actors.db", connect_args={"check_same_thread": False}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
    
    
    actor_id = Column(Integer, ForeignKey("voice_actors.id"))
    
    
    actor = relationship("Voice_Actor", back_populates="characters")
    
    
    episodes = relationship(
        "Episode",
        secondary='character_episode_association',
        back_populates="characters"
    )


class Episode(Base):
    __tablename__ = "episodes"

    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    air_date = Column(String)
    episode_code = Column(String, unique=True) # Ex: S01E01
    
    
    characters = relationship(
        "Character",
        secondary='character_episode_association',
        back_populates="episodes"
    )

character_episode_association = Table(
    'character_episode_association', Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('episode_id', Integer, ForeignKey('episodes.id'), primary_key=True)
)

Base.metadata.create_all(bind=engine)

def populate_database() -> None:
    db = Session()
    
    try:
        # Get lastest data

        my_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'
        tmdb_url = f'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key={my_key}'
        voice_actors: list[dict] = json.loads(request('get', tmdb_url).data)['cast']
        
        char_count_url = 'https://rickandmortyapi.com/api/character'
        characters_count: int = json.loads(request('get', char_count_url).data)['info']['count']
        all_ids = ','.join([str(i) for i in range(1, characters_count + 1)])
        chars_url = f'https://rickandmortyapi.com/api/character/{all_ids}'
        characters_list: list[dict] = json.loads(request('get', chars_url).data)

        ep_count_url = 'https://rickandmortyapi.com/api/episode'
        episodes_count: int = json.loads(request('get', ep_count_url).data)['info']['count']
        all_ep_ids = ','.join([str(i) for i in range(1, episodes_count + 1)])
        episodes_url = f'https://rickandmortyapi.com/api/episode/{all_ep_ids}'
        episodes_list: list[dict] = json.loads(request('get', episodes_url).data)
        
        
        # Filter Voice Actors with actual characters and dict by char

        char_to_va:dict[str, tuple[str, str]] = {}
        for voice_actor in voice_actors:
            
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

            char_to_va.update([(c, (voice_actor['name'], 'https://www.themoviedb.org/person/%s'%(voice_actor['id']))) for c in chars])
        
        # Filter characters that are present in both API's

        c_names:list[str] = [c['name'] for c in characters_list]
        va_to_char:dict[str, tuple[str, list[str]]] = {}
        for c, va in char_to_va.items():
            if c not in c_names:
                continue
            if va[0] not in va_to_char:
                va_to_char[va[0]] = (va[1], [])
            
            va_to_char[va[0]][1].append(c)
        
        
        va_cache: dict[str, Voice_Actor] = {}
        unique_actors = {actor_name:actor_url for actor_name, actor_url, _ in va_to_char.values()}

        for name, url in unique_actors.items():
            va = Voice_Actor(name=name, url=url, characters=[])
            db.add(va)
            # Commit e refresh para obter o ID do ator
            db.commit()
            db.refresh(va)
            va_cache[name] = va

        # 3.2. Inserir Episodes (Todos os episódios da R&M API)
        episode_cache: dict[int, Episode] = {}
        for ep_data in episodes_list:
            # Note: tmdb_rating e tmdb_overview estão nulos por agora.
            ep = Episode(
                id=ep_data['id'],
                name=ep_data['name'],
                air_date=ep_data['air_date'],
                episode_code=ep_data['episode'],
            )
            db.add(ep)
            episode_cache[ep.id] = ep
        
        # Commit para salvar todos os Episódios (importante antes de relacionar)
        db.commit()
        
        print("3. Inserindo Personagens e relações...")

        # 3.3. Inserir Characters e estabelecer as relações
        for char_data in characters_list:
            #char_name_clean = clean_name(char_data['name'])
            char_id = char_data['id']
            
            # Cria o objeto Character
            new_char = Character(
                id=char_id,
                name=char_data['name'],
                status=char_data['status'],
                species=char_data['species'],
                s_type=char_data['type'],
                gender=char_data['gender'],
                origin=char_data['origin']['name'],
                location=char_data['location']['name'],
                image=char_data['image'],
            )

            # Relação 1: N (Personagem -> Voice_Actor)
            # Se o personagem tiver um ator mapeado (filtrado na etapa 2), associa
            if char_name_clean in final_char_map:
                actor_name, _, _ = final_char_map[char_name_clean]
                # Atribui a FK usando o ID do ator já inserido no cache
                new_char.actor_id = va_cache[actor_name].id 

            # Relação N: M (Personagem -> Episode)
            # Conecta o personagem a todos os episódios que ele aparece
            if char_id in char_episodes_map:
                for ep_id in char_episodes_map[char_id]:
                    if ep_id in episode_cache:
                        new_char.episodes.append(episode_cache[ep_id])

            db.add(new_char)

        # 3.4. Commit final para salvar todos os Personagens e associações N:M
        db.commit()
        
        print("✅ Banco de dados populado com sucesso!")
        
    except IntegrityError:
        db.rollback()
        print("⚠️ Erro de Integridade: Parece que você tentou rodar o script novamente sem apagar o DB. Rollback realizado.")
    except Exception as e:
        db.rollback()
        print(f"❌ Ocorreu um erro catastrófico: {e}. Rollback realizado.")
    finally:
        db.close()

if __name__ == '__main__':
    populate_database()