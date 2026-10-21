"""Utilidades de entrada para cargas con tamaño acotado."""

from fastapi import HTTPException, UploadFile


async def read_upload_limited(
    file: UploadFile,
    *,
    max_bytes: int = 25 * 1024 * 1024,
    chunk_bytes: int = 1024 * 1024,
) -> bytes:
    """Lee una carga en bloques y falla con 413 al superar el máximo permitido."""
    chunks: list[bytes] = []
    size = 0
    while chunk := await file.read(chunk_bytes):
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"El archivo excede el máximo permitido de {max_bytes // (1024 * 1024)} MB",
            )
        chunks.append(chunk)
    return b"".join(chunks)
