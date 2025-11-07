from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importar seus componentes (supondo que os modelos e o database.py estão no mesmo nível ou acessíveis)
from database import session, engine, Base # Sua configuração de DB
from database import Voice_Actor, Character, Episode, EpisodeCharacterCast
import crud
import schemas
from database import collect # Sua função de coleta

# Inicializa o FastAPI
app = FastAPI()

# Garante que as tabelas sejam criadas se o arquivo DB não existir
# Isso deve ser feito APÓS definir todos os modelos ORM (models.py)
Base.metadata.create_all(bind=engine) 

# Dependency: Cria uma sessão de DB para cada requisição e a fecha depois
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

# ---------------- ROTAS ----------------

# Rota de Coleta (Para testar e popular o DB)
@app.post("/collect_data/", summary="Roda a coleta de dados e popula o banco.")
def collect_data(db: Session = Depends(get_db)):
    """Roda a função de coleta de dados da Rick and Morty API e TMDB."""
    try:
        collect(db)
        return {"message": "Dados coletados e banco populado com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro durante a coleta: {str(e)}")

# Rota 1: Listar Personagens
@app.get("/characters/", response_model=List[schemas.Character])
def list_characters(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Retorna uma lista paginada de personagens."""
    characters = crud.get_characters(db, skip=skip, limit=limit)
    return characters

# Rota 2: Consultar Ator e Papéis (O endpoint mais importante)
@app.get("/voice_actor/{actor_id}/", response_model=schemas.VoiceActor, summary="Busca um VA e todos os seus papéis (Personagem + Episódio).")
def get_voice_actor_roles(actor_id: int, db: Session = Depends(get_db)):
    """
    Retorna um Voice Actor específico e uma lista de todos os papéis
    que ele desempenhou em diferentes episódios.
    """
    va = crud.get_voice_actor_with_roles(db, actor_id=actor_id)
    if va is None:
        raise HTTPException(status_code=404, detail="Voice Actor não encontrado.")
    return va

# Rota 3: Consultar Episódio e Elenco
@app.get("/episode/{episode_code}/", response_model=schemas.Episode, summary="Busca um episódio e todos os personagens/atores que atuaram nele.")
def get_episode_cast(episode_code: str, db: Session = Depends(get_db)):
    """
    Busca um episódio pelo código (ex: S01E01) e retorna os detalhes
    de todos os personagens e seus respectivos Voice Actors naquele episódio.
    """
    episode = crud.get_episode_with_cast(db, episode_code=episode_code)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episódio não encontrado.")
    return episode