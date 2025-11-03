from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

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
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String) 
    characters = relationship("Character", back_populates="actor")

# 3. Modelo Character (Personagem)
# Detalhes do personagem dublado
class Character(Base):
    __tablename__ = "characters"

    # Dados da API Rick and Morty
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String)
    species = Column(String, index=True) # Importante para o requisito de filtro
    gender = Column(String)
    image = Column(String)
    
    # Chave Estrangeira: Aponta para o Actor que dubla este personagem
    actor_id = Column(Integer, ForeignKey("actors.id"))
    
    # Relação Muitos-para-1: Vários personagens são dublados pelo mesmo ator
    actor = relationship("Actor", back_populates="characters")
    
    # Relação Muitos-para-Muitos: Personagens <-> Episódios
    episodes = relationship(
        "Episode",
        secondary=character_episode_association,
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
        secondary=character_episode_association,
        back_populates="episodes"
    )

# 5. Modelo Metadata (Opcional, para armazenar informações gerais da TMDB)
# Use este modelo para armazenar informações da série como um todo, 
# se você optar por buscar metadados da série "Rick and Morty" na TMDB.
class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String) # Ex: "TMDB_Rick_and_Morty"
    tmdb_id = Column(Integer, unique=True)
    title = Column(String)
    description = Column(Text)