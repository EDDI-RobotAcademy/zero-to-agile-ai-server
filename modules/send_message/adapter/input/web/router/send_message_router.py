from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from modules.auth.adapter.input.auth_middleware import auth_required
from modules.send_message.application.dto.send_message_dto import (
    SendMessageCreateRequest,
    SendMessageUpdateRequest,
    AcceptStatusUpdateRequest,
    SendMessageResponse
)
from modules.send_message.adapter.input.web.response.accepted_proposal_response import AcceptedProposalResponse
from modules.send_message.application.usecase.create_send_message_usecase import CreateSendMessageUseCase
from modules.send_message.application.usecase.get_send_message_usecase import GetSendMessageUseCase
from modules.send_message.application.usecase.update_send_message_usecase import UpdateSendMessageUseCase
from modules.send_message.application.usecase.update_accept_status_usecase import UpdateAcceptStatusUseCase
from modules.send_message.application.usecase.get_accepted_proposals_usecase import GetAcceptedProposalsUseCase
from modules.send_message.adapter.input.web.dependencies import (
    get_create_send_message_usecase_dep,
    get_get_send_message_usecase_dep,
    get_update_send_message_usecase_dep,
    get_update_accept_status_usecase_dep,
    get_get_accepted_proposals_usecase_dep
)

router = APIRouter(prefix="/messages", tags=["Send Message"])

@router.post(
    "",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="메시지 전송",
    description="임차인은 임대인에게, 임대인은 임차인에게 메시지를 전송합니다."
)
def create_message(
    request: SendMessageCreateRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: CreateSendMessageUseCase = Depends(get_create_send_message_usecase_dep)
):
    try:
        return usecase.execute(abang_user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get(
    "/sent",
    response_model=List[SendMessageResponse],
    summary="보낸 메시지함",
    description="내가 보낸 메시지 목록을 조회합니다."
)
def get_sent_messages(
    abang_user_id: int = Depends(auth_required),
    usecase: GetSendMessageUseCase = Depends(get_get_send_message_usecase_dep)
):
    return usecase.get_sent_messages(abang_user_id)

@router.get(
    "/received",
    response_model=List[SendMessageResponse],
    summary="받은 메시지함",
    description="내가 받은 메시지 목록을 조회합니다."
)
def get_received_messages(
    abang_user_id: int = Depends(auth_required),
    usecase: GetSendMessageUseCase = Depends(get_get_send_message_usecase_dep)
):
    return usecase.get_received_messages(abang_user_id)

@router.put(
    "/content",
    response_model=SendMessageResponse,
    summary="메시지 내용 수정",
    description="보낸 메시지의 내용을 수정합니다. (송신자만 가능, ID는 Body에 포함)"
)
def update_message_content(
    request: SendMessageUpdateRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: UpdateSendMessageUseCase = Depends(get_update_send_message_usecase_dep)
):
    try:
        # UseCase expects (user_id, message_id, request_dto)
        return usecase.execute(abang_user_id, request.send_message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get(
    "/accepted",
    response_model=List[AcceptedProposalResponse],
    summary="수락한 제안 목록 조회",
    description="내가 수락한 제안(매물 또는 의뢰서)의 상세 정보를 조회합니다."
)
def get_accepted_proposals(
    abang_user_id: int = Depends(auth_required),
    usecase: GetAcceptedProposalsUseCase = Depends(get_get_accepted_proposals_usecase_dep)
):
    return usecase.execute(abang_user_id)

@router.put(
    "/status",
    response_model=SendMessageResponse,
    summary="제안 수락/거절 상태 변경",
    description="받은 제안의 상태를 변경합니다. (수락: 'Y', 거절: 'N', 대기: 'W'). 수신자만 가능합니다."
)
def update_accept_status(
    request: AcceptStatusUpdateRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: UpdateAcceptStatusUseCase = Depends(get_update_accept_status_usecase_dep)
):
    try:
        return usecase.execute(abang_user_id, request.send_message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete(
    "/{send_message_id}",
    response_model=SendMessageResponse,
    summary="받은 제안 삭제 (Soft Delete)",
    description="받은 제안을 삭제(상태를 'D'로 변경)합니다. 수신자만 가능합니다."
)
def delete_received_message(
    send_message_id: int,
    abang_user_id: int = Depends(auth_required),
    usecase: UpdateAcceptStatusUseCase = Depends(get_update_accept_status_usecase_dep)
):
    try:
        # 'D' 상태로 변경하기 위한 요청 객체 생성
        request = AcceptStatusUpdateRequest(
            send_message_id=send_message_id,
            accept_type='D'
        )
        return usecase.execute(abang_user_id, send_message_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))