import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.deps import SessionDep, get_current_author, CurrentUser
from app.schemas.post import PostCreate, PostResponse, PostUpdate, PostSummaryResponse, PostQuestionAnswerRequest
from app.crud import post as post_crud
from app.models.post import PostStatus
from app.genai.services.summarization import SummarizationService

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/",dependencies=[Depends(get_current_author)], status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(db: SessionDep, author : CurrentUser, post_data: PostCreate):
    """
    ## Creates a new post.

    This route takes a JSON body that contains the post data.

    ### Request Body:
    - **title** (`str`): The title of the post.
    - **content** (`str`): The content of the post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the post.
    - **status** (`PostStatus`): The status of the post. Possible values are `DRAFT` or `PUBLISHED`.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the created post.
    - **title** (`str`): The title of the created post.
    - **content** (`str`): The content of the created post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the created post.
    - **status** (`PostStatus`): The status of the post. Possible values are `DRAFT` or `PUBLISHED`.
    - **author_id** (`uuid.UUID`): The ID of the author of the created post.
    """
    return post_crud.create_post(db=db, author=author, post_data=post_data)


@router.get("/{post_id}", response_model=PostResponse)
def read_post(db: SessionDep, post_id: str):
    """
    ## Reads a post by its ID.

    This route takes a path parameter that is the post ID.

    ### Path:
    - **post_id** (`str`): The ID of the post to read.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the post status is DRAFT.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the post.
    - **title** (`str`): The title of the post.
    - **content** (`str`): The content of the post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the post.
    - **status** (`PostStatus`): The status of the post.
    - **author_id** (`uuid.UUID`): The ID of the author of the post.
    """

    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    print(type(post.status))
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.status == PostStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse, dependencies=[Depends(get_current_author)])
def update_post(db: SessionDep, author: CurrentUser, post_id: str, post_data: PostUpdate):
    """
    ## Updates a post by its ID.

    This route takes a path parameter that is the post ID and a JSON body that contains the updated post data.

    ### Path:
    - **post_id** (`str`): The ID of the post to update.

    ### Request Body:
    - **title** (`Optional[str]`): The updated title of the post.
    - **content** (`Optional[str]`): The updated content of the post.
    - **tags_list** (`Optional[List[str]]`): The updated list of tags for the post.
    - **status** (`Optional[PostStatus]`): The updated status of the post.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the user is not authorized to update the post.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the updated post.
    - **title** (`str`): The title of the updated post.
    - **content** (`str`): The content of the updated post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the updated post.
    - **status** (`PostStatus`): The status of the updated post.
    - **author_id** (`uuid.UUID`): The ID of the author of the updated post.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.author_id != author.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update post")
    
    return post_crud.update_post(db=db, post=post, post_data=post_data)


@router.get("/", response_model=List[PostResponse])
def read_posts(db: SessionDep):

    """
    ## Reads all published posts.

    This route does not take any parameters.

    ### Response Body:
    - **List[PostResponse]**: A list of all published posts.
        - **id** (`uuid.UUID`): The ID of the post.
        - **title** (`str`): The title of the post.
        - **content** (`str`): The content of the post.
        - **tags_list** (`Optional[List[str]]`): The list of tags for the post.
        - **status** (`PostStatus`): The status of the post.
        - **author_id** (`uuid.UUID`): The ID of the author of the post.
    """
    return post_crud.get_posts(db=db)



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