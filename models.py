# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

# 1. Tabela de Associação Muitos-para-Muitos (Episode <-> Character)
# Os personagens aparecem em vários episódios e os episódios têm vários personagens.
character_episode_association = Table(
    'character_episode',
    Base.metadata,
    Column('episode_id', Integer, ForeignKey('episodes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

# 2. Modelo Actor (Dublador)
# O dublador (Actor) é o elo principal para os endpoints /voice_actor/*
class Actor(Base):
    __tablename__ = "actors"

    # Dados da API Rick and Morty, onde 'name' seria o nome do ator/dublador
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    # URL de outros dados do ator, se necessário
    url = Column(String) 
    
    # Relação 1-para-Muitos: Um ator dubla vários personagens
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