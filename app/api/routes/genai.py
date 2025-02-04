import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.genai.services.summarization import SummarizationService
from app.schemas.post import PostSummaryResponse, PostQuestionAnswerRequest
from app.models.post import PostStatus
from app.crud import post as post_crud

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/{post_id}/summarize", response_model=PostSummaryResponse)
def summarize_post(db: SessionDep, post_id: str):
    """
    ## Summarizes a post by its ID.

    This route takes a path parameter that is the post ID and returns a summary of the post.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to summarize.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found or is a draft.

    ### Response Body:
    - **summary** (`str`): The summary of the post.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None or post.status == PostStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    summary = SummarizationService().summarize(content=post.content)
    return summary
    

@router.get("/{post_id}/chat")
def chat_with_post(db: SessionDep, post_id: str, current_user: CurrentUser, question_data: PostQuestionAnswerRequest):
    """
    ## Chat with a post.

    This route takes a path parameter that is the post ID and returns a chat interface to interact with the post.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to chat with.
    """

    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return {"message": "Chat with post"}