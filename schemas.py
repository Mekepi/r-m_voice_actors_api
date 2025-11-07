from pydantic import BaseModel
from typing import Optional, List

# ------------------ Base Schemas (Dados Brutos) ------------------

class VoiceActorBase(BaseModel):
    id: int
    name: str
    original_name: Optional[str] = None
    gender: Optional[int] = None

class CharacterBase(BaseModel):
    id: int
    name: str
    species: str
    status: Optional[str] = None
    gender: Optional[str] = None

class EpisodeBase(BaseModel):
    id: int
    episode_code: str
    name: str
    air_date: str

# ------------------ Objeto de Associação (Role) ------------------

class Role(BaseModel):
    # Usado para exibir a relação completa de atuação
    episode_id: int
    character_id: int
    
    # Adicionando a classe 'Config' para que o Pydantic saiba lidar
    # com os objetos ORM (SQLAlchemy)
    class Config:
        from_attributes = True # FastAPI 0.100.0+ usa from_attributes = True

# ------------------ Schemas de Resposta (Relacionamentos) ------------------

# 1. Schema para o Voice Actor (inclui os papéis detalhados)
class VoiceActor(VoiceActorBase):
    # A lista de papéis (EpisodeCharacterCast) feitos por este ator
    episode_roles: List['RoleDetail'] = [] 
    
    class Config:
        from_attributes = True

# 2. Schema para o Personagem (inclui apenas dados simples, para evitar loops circulares)
class Character(CharacterBase):
    # Não incluir a lista de roles aqui para não criar um loop de referência
    pass

# 3. Schema para o Episódio (inclui o elenco que atuou nele)
class Episode(EpisodeBase):
    character_roles: List['RoleDetail'] = []
    
    class Config:
        from_attributes = True

# 4. Detalhe do Papel (RoleDetail) - Onde a mágica acontece
class RoleDetail(Role):
    # O Pydantic carregará o objeto completo através da relação ORM
    episode: EpisodeBase 
    character: CharacterBase
    voice_actor: Optional[VoiceActorBase] = None
    
    class Config:
        from_attributes = True

# Atualiza referências circulares
VoiceActor.model_rebuild()