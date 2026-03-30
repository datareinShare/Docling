import base64
import tempfile
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from docling.document_converter import DocumentConverter

app = FastAPI(title="Docling API")
converter = DocumentConverter()


class UrlRequest(BaseModel):
    url: str
    format: str = "markdown"


class Base64Request(BaseModel):
    data: str
    filename: str
    format: str = "markdown"


def export_result(result, fmt: str) -> str:
    if fmt == "markdown":
        return result.document.export_to_markdown()
    elif fmt == "text":
        return result.document.export_to_text()
    elif fmt == "doctags":
        return result.document.export_to_document_tokens()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convert/url")
def convert_url(req: UrlRequest):
    try:
        result = converter.convert(req.url)
        content = export_result(result, req.format)
        return {"content": content, "format": req.format}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/base64")
def convert_base64(req: Base64Request):
    try:
        file_bytes = base64.b64decode(req.data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / req.filename
        filepath.write_bytes(file_bytes)
        try:
            result = converter.convert(str(filepath))
            content = export_result(result, req.format)
            return {"content": content, "format": req.format}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/file")
def convert_file(
    file: UploadFile = File(...),
    format: str = Form("markdown"),
):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / (file.filename or "upload")
        filepath.write_bytes(file.file.read())
        try:
            result = converter.convert(str(filepath))
            content = export_result(result, format)
            return {"content": content, "format": format}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
