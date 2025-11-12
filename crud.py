from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Voice_Actor, Character, Episode, EpisodeCharacterCast # Seus modelos ORM
from typing import Optional

def get_all_voice_actors(db:Session) -> list[Voice_Actor]:
    return db.query(Voice_Actor).all()

def get_voice_actor(db: Session, va_id: int, char_b:bool=False, ep_b:bool=False, ep_char_b:bool=False) -> tuple[Voice_Actor, list[Character], list[Episode], list[tuple[Episode, Character]]]|tuple[None, None, None, None]:
    va:Voice_Actor|None = db.query(Voice_Actor).filter(Voice_Actor.id == va_id).first()

    if not(isinstance(va, Voice_Actor)):
        return (None, None, None, None)
    
    chars:list[Character] = []
    if char_b:
        chars_id:list[int] = list(db.scalars(
                select(EpisodeCharacterCast.character_id)
                .where(EpisodeCharacterCast.voice_actor_id == va_id)
                .distinct()
            ).all())
        
        chars = list(db.scalars(
            select(Character)
            .where(Character.id.in_(chars_id))
        ))
    
    eps:list[Episode] = []
    if ep_b:
        eps_id:list[int] = list(db.scalars(
            select(EpisodeCharacterCast.episode_id)
            .where(EpisodeCharacterCast.voice_actor_id == va_id)
            .distinct()
        ).all())
    
        eps = list(db.scalars(
            select(Episode)
            .where(Episode.id.in_(eps_id))
        ))

    eps_char:list[tuple[Episode, Character]] = []
    """ if ep_char_b:
        eps_char_id:list[tuple[int, int]] = list(db.scalars(
            select(EpisodeCharacterCast.episode_id, EpisodeCharacterCast.character_id)
            .where(EpisodeCharacterCast.voice_actor_id == va_id)
            .distinct()
        ).all())

        for epid, charid in eps_char_id:
            eps_char.append(
                (
                db.scalars(select(Episode).where(Episode.id == epid)).first(),
                db.scalars(select(Character).where(Character.id == charid)).first()
                )
            ) """
    
    return (va, chars, eps, eps_char)