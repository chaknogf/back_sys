import os
import csv
import io
import urllib.request
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text

from sqlalchemy import inspect

from core.database import engine, Base
from modules.cie10.models import Cie10Model
from core.config import (
    CIE10_LLM_API_KEY, CIE10_LLM_MODEL, CIE10_LLM_PROVIDER,
    CIE10_LLM_BASE_URL, OLLAMA_HOST,
)


CSV_URL = "https://github.com/verasativa/CIE-10/raw/master/cie-10.csv"


def asegurar_tabla():
    if not inspect(engine).has_table("cie10_catalogo"):
        Cie10Model.__table__.create(engine)


def descargar_catalogo(db: Session) -> int:
    existe = db.query(Cie10Model).first()
    if existe:
        total = db.query(Cie10Model).count()
        return total

    resp = urllib.request.urlopen(CSV_URL)
    contenido = resp.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contenido))

    count = 0
    for row in reader:
        codigo = row.get("code", "").strip()
        descripcion = row.get("description", "").strip()
        nivel_str = row.get("level", "0").strip()
        fuente = row.get("source", "").strip()
        codigo_padre = None
        nivel = int(nivel_str) if nivel_str.isdigit() else 0

        for level in range(nivel - 1, -1, -1):
            parent = row.get(f"code_{level}", "").strip()
            if parent:
                codigo_padre = parent
                break

        if not codigo or not descripcion:
            continue

        existe = db.query(Cie10Model).filter(Cie10Model.codigo == codigo).first()
        if existe:
            continue

        registro = Cie10Model(
            codigo=codigo,
            descripcion=descripcion,
            nivel=nivel,
            codigo_padre=codigo_padre,
            fuente=fuente,
        )
        db.add(registro)
        count += 1

        if count % 500 == 0:
            db.flush()

    db.commit()
    return count


def asegurar_catalogo(db: Session) -> int:
    asegurar_tabla()
    total = db.query(Cie10Model).count()
    if total == 0:
        total = descargar_catalogo(db)
    return total


def _unaccent_ilike(column, pattern: str):
    return func.unaccent(column).ilike(f"%{pattern}%")


def buscar_cie10(
    db: Session,
    q: str,
    nivel: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[Cie10Model], int]:

    query = db.query(Cie10Model)

    terms = [t.strip() for t in q.split() if t.strip()]
    if terms:
        filters = []
        for term in terms:
            filters.append(
                or_(
                    Cie10Model.codigo.ilike(f"%{term}%"),
                    _unaccent_ilike(Cie10Model.descripcion, term),
                )
            )
        query = query.filter(or_(*filters))

    if nivel is not None:
        query = query.filter(Cie10Model.nivel == nivel)

    total = query.count()
    resultados = (
        query.order_by(Cie10Model.nivel, Cie10Model.codigo)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return resultados, total


def buscar_relevantes(
    db: Session, pregunta: str, limite: int = 10
) -> List[Cie10Model]:
    tokens = [t.strip().upper() for t in pregunta.split() if len(t.strip()) > 2]
    if not tokens:
        return []

    query = db.query(Cie10Model)
    filtros = []
    for token in tokens:
        filtros.append(
            or_(
                Cie10Model.codigo.ilike(f"%{token}%"),
                _unaccent_ilike(Cie10Model.descripcion, token),
            )
        )
    query = query.filter(or_(*filtros))
    return query.order_by(Cie10Model.nivel).limit(limite).all()


def _construir_contexto(
    pregunta: str,
    codigos_contexto: Optional[List[str]] = None,
    db: Optional[Session] = None,
) -> str:
    if codigos_contexto and db:
        codigos = (
            db.query(Cie10Model)
            .filter(Cie10Model.codigo.in_(codigos_contexto))
            .all()
        )
    elif db:
        codigos = buscar_relevantes(db, pregunta)
    else:
        codigos = []

    contexto = ""
    if codigos:
        contexto = "\nCódigos CIE-10 relevantes encontrados en el catálogo local:\n"
        for c in codigos:
            contexto += f"- {c.codigo}: {c.descripcion}\n"
    return contexto


SISTEMA_PROMPT = (
    "Eres un asistente experto en codificación CIE-10 (Clasificación "
    "Internacional de Enfermedades, 10ª revisión). Responde preguntas "
    "sobre diagnósticos médicos y sus códigos CIE-10 en español.\n\n"
    "Reglas:\n"
    "- Usa los códigos del catálogo local incluidos abajo como fuente principal.\n"
    "- Si mencionas un código CIE-10, incluye también su descripción.\n"
    "- Reconoce abreviaturas médicas comunes (IAM, EPOC, DM2, HTA, IRC, TVP, etc.)\n"
    "- Reconoce nombres coloquiales de enfermedades y procedimientos.\n"
    "- Si no sabes la respuesta o el código no está en el catálogo, dilo honestamente.\n"
    "- Responde en español, de forma clara y concisa.\n"
)


def _construir_mensajes(
    mensajes: List[dict],
    contexto: str,
) -> List[dict]:
    system = {"role": "system", "content": SISTEMA_PROMPT + "\n" + contexto}
    return [system] + mensajes


def _llm_ollama(messages: List[dict]) -> str:
    import httpx
    model = CIE10_LLM_MODEL if CIE10_LLM_MODEL != "gpt-4o-mini" else "phi3:mini"
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    with httpx.Client(timeout=120) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()


def _llm_gemini(messages: List[dict]) -> str:
    import httpx
    model = CIE10_LLM_MODEL if CIE10_LLM_MODEL != "gpt-4o-mini" else "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    system_text = ""
    contents_parts = []
    for msg in messages:
        if msg["role"] == "system":
            system_text += msg["content"] + "\n"
        elif msg["role"] == "user":
            contents_parts.append({"role": "user", "parts": [{"text": system_text + msg["content"]}]})
            system_text = ""
        elif msg["role"] == "assistant":
            contents_parts.append({"role": "model", "parts": [{"text": msg["content"]}]})

    if not contents_parts:
        contents_parts = [{"parts": [{"text": system_text}]}]

    payload = {
        "contents": contents_parts,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000},
    }
    headers = {"Content-Type": "application/json", "X-goog-api-key": CIE10_LLM_API_KEY}
    with httpx.Client(verify=True, timeout=30) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        textos = []
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                textos.append(part.get("text", ""))
        return "\n".join(textos)


def _llm_openai(messages: List[dict]) -> str:
    import httpx
    model = CIE10_LLM_MODEL
    api_url = f"{CIE10_LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {CIE10_LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1000,
    }
    with httpx.Client(verify=True, timeout=60) as client:
        resp = client.post(api_url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


PROVIDERS = {
    "ollama": _llm_ollama,
    "gemini": _llm_gemini,
    "openai": _llm_openai,
}


def responder_pregunta(
    mensajes: List[dict],
    codigos_contexto: Optional[List[str]] = None,
    db: Optional[Session] = None,
) -> str:
    ultimo_user = next(
        (m["content"] for m in reversed(mensajes) if m["role"] == "user"),
        "",
    )
    contexto = _construir_contexto(ultimo_user, codigos_contexto, db)
    mensajes_con_sistema = _construir_mensajes(mensajes, contexto)

    provider = CIE10_LLM_PROVIDER
    if provider == "ollama":
        try:
            return _llm_ollama(mensajes_con_sistema)
        except Exception:
            if CIE10_LLM_API_KEY:
                provider = "gemini" if CIE10_LLM_API_KEY.startswith("AIza") else "openai"
            else:
                raise ValueError(
                    "Ollama no está disponible. "
                    "Instálalo con: brew install ollama && ollama pull phi3:mini"
                )

    llm_fn = PROVIDERS.get(provider)
    if not llm_fn:
        raise ValueError(
            f"Proveedor desconocido: {provider} "
            f"(usa 'ollama', 'openai' o 'gemini')"
        )
    return llm_fn(mensajes_con_sistema)
