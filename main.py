from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import session, engine, Base
from database import Voice_Actor, Character, Episode, EpisodeCharacterCast
import crud
import schemas
from database import collect # Sua função de coleta

app = FastAPI()

Base.metadata.create_all(bind=engine) 

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

################################

@app.get("/collect", summary='(Re)Popula o banco de dados')
def collect_data(db:Session = Depends(get_db)):
    try:
        collect(db)
        return {"message": "Dados coletados e banco de dados populado com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = 500, detail = f"Erro durante a coleta: {str(e)}")


@app.get("/voice_actor/list", summary = 'Retorna todos os dubladores e seus papeis')
def get_voice_actor_list(db: Session = Depends(get_db)):
    vas = crud.get_all_voice_actors(db)

    vas_chars:list[schemas.myVoiceActor] = []
    for va in vas:
        vab, charsb, _, _= crud.get_voice_actor(db, int(va.id), char_b=True)
        if (not(isinstance(vab, Voice_Actor))):
            continue
        
        chars:list[schemas.myCharacter] = [schemas.myCharacter(c) for c in charsb]
        vasch:schemas.myVoiceActor = schemas.myVoiceActor(vab, chars)
        vas_chars.append(vasch)

    if not(vas_chars):
        raise HTTPException(status_code = 404, detail = "Dubladores não encontrados")
    
    return vas_chars

@app.get("/voice_actor/{va_id}", summary = "Busca um dublador")
def get_voice_actor(va_id:int, db:Session = Depends(get_db)):
    va, _, _, eps_cha = crud.get_voice_actor(db, va_id, ep_char_b=True)

    if not(isinstance(va, Voice_Actor)):
        raise HTTPException(status_code=404, detail="Dublador não encontrado.")
    
    return schemas.myVoiceActor(va)


@app.get("/voice_actor/{va_id}/acted_in", summary = "Busca um dublador e os episódios em que atuou")
def get_voice_actor_episodes_in(va_id:int, db:Session = Depends(get_db)):
    va, _, eps, _ = crud.get_voice_actor(db, va_id, ep_b=True)

    if not(va):
        raise HTTPException(status_code=404, detail="Dublador não encontrado.")

    vasch:schemas.myVoiceActor = schemas.myVoiceActor(va, episodes=[schemas.myEpisode(ep) for ep in eps])
        
    return vasch.episodes_in

@app.get("/voice_actor/{va_id}/characters", summary = "Busca um dublador e os personagens que dublou")
def get_voice_actor_characters(va_id:int, db:Session = Depends(get_db)):
    vab, charsb, _, _ = crud.get_voice_actor(db, va_id, char_b=True)

    if not(vab):
        raise HTTPException(status_code=404, detail="Dublador não encontrado.")
    
    vasch:schemas.myVoiceActor = schemas.myVoiceActor(vab, chars=[schemas.myCharacter(c) for c in charsb])
        
    return vasch.characters
