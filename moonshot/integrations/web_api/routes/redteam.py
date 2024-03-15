# api/routes.py
import logging
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from dependency_injector.wiring import inject, Provide
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..schemas.prompt_response_model import PromptResponseModel
from ..container import Container
from ..services.utils.exceptions_handler import SessionException
from ..schemas.session_response_model import SessionMetadataModel, SessionResponseModel
from ..schemas.session_create_dto import SessionCreateDTO
from ..schemas.session_prompt_dto import SessionPromptDTO
from ..services.session_service import SessionService, PromptDetails

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
@inject
async def status(asyncio_monitor_task = Depends(Provide[Container.config.log.level])):
    logger.warn(asyncio_monitor_task)
    return {"status": "web api is up and running"}


@router.get("/v1/sessions")
@inject
async def get_all_sessions(
    session_service: SessionService = Depends(Provide[Container.session_service])
) -> list[Optional[SessionMetadataModel]]:
    try:
        return session_service.get_sessions()
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)


@router.get("/v1/sessions/{session_id}")
@inject
async def get_session_by_session_id(
    session_id: str,
    include_history: bool = False,
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> SessionResponseModel:
    try:
        session_data = session_service.get_session(session_id)
        if include_history:
            history = session_service.get_session_chat_history(session_id)
            if session_data is not None:
                session_data.chat_history = history
        if session_data is not None:
            return SessionResponseModel(session=session_data)
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)


@router.post("/v1/sessions")
@inject
async def create(
    session_dto: SessionCreateDTO,
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> SessionResponseModel:
    try: 
        new_session = session_service.create_session(session_dto)
        updated_with_chat_ids = session_service.get_session(new_session.session_id)
        return SessionResponseModel(session=updated_with_chat_ids)
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)

@router.post("/v1/sessions/{session_id}/prompt")
@inject
async def prompt(
    session_id: str,
    user_prompt: SessionPromptDTO,
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> PromptResponseModel:
    try:
        result = await session_service.send_prompt(session_id, user_prompt.prompt)
        return result
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)


@router.get("/v1/prompt_templates")
@inject
def get_all_prompt_templates(
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> list[Optional[Any]]:
    """
    Get all the prompt templates from the database
    """
    try:
        return session_service.get_prompt_templates()
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)


@router.put("/v1/sessions/{session_id}/prompt_templates/{prompt_template_name}")
@inject
async def set_prompt_template(
    session_id: str,
    prompt_template_name: str,
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> dict[str, bool]:
    """
    Select a prompt template for the current session
    """
    try:
        result = session_service.select_prompt_template(session_id,prompt_template_name)
        return {"success": result}
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)


@router.delete("/v1/sessions/{session_id}/prompt_templates/{prompt_template_name}")
@inject
async def unset_prompt_template(
    session_id: str,
    prompt_template_name: str = '',
    session_service: SessionService = Depends(Provide[Container.session_service])
    ) -> dict[str, bool]:
    """
    Remove prompt template from the current session
    """
    try:
        result = session_service.select_prompt_template(session_id,"")
        return {"success": result}
    except SessionException as e:
        if e.error_code == "FileNotFound":
            raise HTTPException(status_code=404, detail=e.msg)
        elif e.error_code == "ValidationError":
            raise HTTPException(status_code=400, detail=e.msg)
        else:
            raise HTTPException(status_code=500, detail=e.msg)