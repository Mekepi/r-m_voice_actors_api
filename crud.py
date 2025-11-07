from sqlalchemy.orm import Session
from database import Voice_Actor, Character, Episode, EpisodeCharacterCast # Seus modelos ORM
from typing import List, Optional

# Função de leitura: Busca um ator pelo ID e seus papéis completos
def get_voice_actor_with_roles(db: Session, actor_id: int) -> Optional[Voice_Actor]:
    # O .options(joinedload(...)) é opcional, mas otimiza a consulta (eager loading)
    return db.query(Voice_Actor).filter(Voice_Actor.id == actor_id).first()

# Função de leitura: Busca um episódio e seu elenco
def get_episode_with_cast(db: Session, episode_code: str) -> Optional[Episode]:
    return db.query(Episode).filter(Episode.episode_code == episode_code).first()

# Função de leitura: Busca todos os personagens
def get_characters(db: Session, skip: int = 0, limit: int = 100) -> List[Character]:
    return db.query(Character).offset(skip).limit(limit).all()

# Função de criação: Executa a coleta (você já tem a lógica em collect!)
# def run_collection(db: Session) -> None:
#     # Aqui você chamaria sua função collect(db)
#     pass