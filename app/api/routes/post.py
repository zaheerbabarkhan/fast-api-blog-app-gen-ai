from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from fastapi.responses import JSONResponse

from app.api.deps import get_current_author, CurrentUser, get_current_user
from app.exceptions.exceptions import AppBaseException, ForbiddenException, ResourceNotFoundException
from app.schemas.post import PostCreate, PostListResponse, PostQuestionAnswerRequest, PostResponse, PostSuggestionsRequest, PostSuggestionsResponse, PostSummaryResponse, PostUpdate
from app.schemas.comment import CommentCreateRequest, CommentResponse, CommentResponseWithReplies
from app.services.comment import CommentService
from app.services.post import PostService
from app.services.question_answer.question_answer import QuestionAnswerService
from app.services.suggestion import SuggestionService
from app.services.summarization import SummarizationService

router = APIRouter(prefix="/posts")

@router.post("/", dependencies=[Depends(get_current_author)], status_code=status.HTTP_201_CREATED, response_model=PostResponse, tags=["Author"])
def create_post(post_data: PostCreate, author: CurrentUser, post_service: PostService = Depends()):
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
    try:
        return post_service.create_post(author=author, post_data=post_data)
    except AppBaseException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch posts, please try again later or contact support")

@router.get("/{post_id}", response_model=PostResponse, tags=["Public Post"])
def get_post(post_id: UUID, post_service: PostService = Depends()):
    """
    ## Fetches a post by ID.

    This route takes a post ID as a path parameter.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to fetch.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the post status is DRAFT.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the fetched post.
    - **title** (`str`): The title of the fetched post.
    - **content** (`str`): The content of the fetched post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the fetched post.
    - **status** (`PostStatus`): The status of the post. Possible values are `DRAFT` or `PUBLISHED`.
    - **author_id** (`uuid.UUID`): The ID of the author of the fetched post.
    """
    try:
        return post_service.get_post(post_id=post_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch post, please try again later or contact support")

@router.put("/{post_id}", response_model=PostResponse, dependencies=[Depends(get_current_author)], tags=["Author"])
def update_post(post_id: UUID, post_data: PostUpdate, post_service: PostService = Depends()):
    """
    ## Updates a post by ID.

    This route takes a post ID as a path parameter and a JSON body that contains the updated post data.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to update.

    ### Request Body:
    - **title** (`Optional[str]`): The updated title of the post.
    - **content** (`Optional[str]`): The updated content of the post.
    - **tags_list** (`Optional[List[str]]`): The updated list of tags for the post.
    - **status** (`Optional[PostStatus]`): The updated status of the post. Possible values are `DRAFT` or `PUBLISHED`.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the updated post.
    - **title** (`str`): The title of the updated post.
    - **content** (`str`): The content of the updated post.
    - **tags_list** (`Optional[List[str]]`): The list of tags for the updated post.
    - **status** (`PostStatus`): The status of the post. Possible values are `DRAFT` or `PUBLISHED`.
    - **author_id** (`uuid.UUID`): The ID of the author of the updated post.
    """
    try:
        return post_service.update_post(post_id=post_id, post_data=post_data)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to update post, please try again later or contact support")

@router.delete("/{post_id}", tags=["Author"], response_model=PostResponse)
def delete_post(post_id: UUID, current_user: CurrentUser, post_service: PostService = Depends()):
    """
    ## Deletes a post by ID.

    This route takes a post ID as a path parameter.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to delete.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the user is not authorized to delete the post.
    """
    try:
        post_service.delete_post(post_id=post_id, current_user=current_user)

        return JSONResponse("Post deleted successfully", status_code=status.HTTP_200_OK)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to delete post, please try again later or contact support")

@router.get("/", response_model=List[PostListResponse], tags=["Public Post"])
def get_posts(post_service: PostService = Depends()):
    """
    ## Fetches all posts.

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
    try:
        return post_service.get_posts()
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch posts, please try again later or contact support")

@router.post("/{post_id}/comments", response_model=CommentResponse, tags=["Comment"])
def create_comment(post_id: UUID, comment_data: CommentCreateRequest, current_user: CurrentUser, comment_service: CommentService = Depends()):
    """
    ## Creates a new comment on a post.

    This route takes a post ID as a path parameter and a JSON body that contains the comment data.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to comment on.

    ### Request Body:
    - **content** (`str`): The content of the comment.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the created comment.
    - **content** (`str`): The content of the created comment.
    - **author_id** (`uuid.UUID`): The ID of the author of the created comment.
    - **post_id** (`uuid.UUID`): The ID of the post the comment is associated with.
    """
    try:
        return comment_service.create_comment(post_id=post_id, comment_data=comment_data, author=current_user)
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to add comment, please try again later or contact support")

@router.get("/{post_id}/comments", response_model=List[CommentResponseWithReplies], tags=["Comment"], dependencies=[Depends(get_current_user)])
def get_comments(post_id: UUID, comment_service: CommentService = Depends()):
    """
    ## Fetches all comments on a post.

    This route takes a post ID as a path parameter.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to fetch comments for.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.

    ### Response:
    - **List[CommentResponse]**: A list of comments on the post.
        - **id** (`uuid.UUID`): The ID of the comment.
        - **content** (`str`): The content of the comment.
        - **post_id** (`uuid.UUID`): The ID of the post the comment belongs to.
        - **author_id** (`uuid.UUID`): The ID of the author of the comment.
    """
    try:
        return comment_service.get_post_comments(post_id=post_id)
    
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch comments, please try again later or contact support")

@router.post("/comments/{comment_id}/reply", response_model=CommentResponse, tags=["Comment"])
def reply_to_comment(comment_id: UUID, comment_data: CommentCreateRequest, current_user: CurrentUser, comment_service: CommentService = Depends()):
    """
    ## Replies to a comment on a post.

    This route takes a post ID and a comment ID as path parameters and a JSON body that contains the reply data.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post the comment is associated with.
    - **comment_id** (`uuid.UUID`): The ID of the comment to reply to.

    ### Request Body:
    - **content** (`str`): The content of the reply.

    ### Raises:
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the created reply.
    - **content** (`str`): The content of the created reply.
    - **author_id** (`uuid.UUID`): The ID of the author of the created reply.
    - **post_id** (`uuid.UUID`): The ID of the post the reply is associated with.
    - **parent_comment_id** (`uuid.UUID`): The ID of the parent comment.
    """
    try:
        return comment_service.reply_to_comment(comment_id=comment_id, reply_data=comment_data, author=current_user)
    
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to reply to comment, please try again later or contact support")

@router.delete("/comments/{comment_id}", tags=["Comment"])
def delete_comment(comment_id: UUID, current_user: CurrentUser, comment_service: CommentService = Depends()):
    """
    ## Deletes a comment by ID.

    This route takes a comment ID as a path parameter.

    ### Path Parameters:
    - **comment_id** (`uuid.UUID`): The ID of the comment to delete.

    ### Raises:
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.
    - **HTTPException**: If the user is not authorized to delete the comment.
    """
    try:
        comment_service.delete_comment(comment_id=comment_id, current_user=current_user)

        return JSONResponse("Comment deleted successfully", status_code=status.HTTP_200_OK)
    
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to delete comment, please try again later or contact support")

@router.put("/comments/{comment_id}", response_model=CommentResponse, tags=["Comment"])
def update_comment(comment_id: UUID, comment_data: CommentCreateRequest, current_user: CurrentUser, post_service: PostService = Depends()):
    """
    ## Updates a comment by ID.

    This route takes a comment ID as a path parameter and a JSON body that contains the updated comment data.

    ### Path Parameters:
    - **comment_id** (`uuid.UUID`): The ID of the comment to update.

    ### Request Body:
    - **content** (`str`): The updated content of the comment.

    ### Raises:
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.
    - **HTTPException**: If the user is not authorized to update the comment.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the updated comment.
    - **content** (`str`): The content of the updated comment.
    - **author_id** (`uuid.UUID`): The ID of the author of the updated comment.
    - **post_id** (`uuid.UUID`): The ID of the post the comment is associated with.
    """
    try:
        return post_service.update_comment(comment_id=comment_id, comment_data=comment_data)
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to update comment, please try again later or contact support")

@router.get("/{post_id}/summarize", response_model=PostSummaryResponse, tags=["LLM"])
def summarize_post(post_id: UUID, post_service: PostService = Depends()):
    """
    ## Summarizes a post by ID.

    This route takes a post ID as a path parameter.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to summarize.

    ### Response Body:
    - **summary** (`str`): The summary of the post.
    """
    try:
        return post_service.summarize_post(post_id=post_id)
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to summarize post, please try again later or contact support")

@router.post("/{post_id}/chat", tags=["LLM"])
def chat_with_post(post_id: UUID, question_data: PostQuestionAnswerRequest, current_user: CurrentUser, post_service: PostService = Depends()):
    """
    ## Chats with a post by ID.

    This route takes a post ID as a path parameter and a JSON body that contains the question data.

    ### Path Parameters:
    - **post_id** (`uuid.UUID`): The ID of the post to chat with.

    ### Request Body:
    - **question** (`str`): The question to ask the post.
    """
    try:
        return post_service.chat_with_post(post_id=post_id, question=question_data.question, current_user=current_user)
    
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to answer question, please try again later or contact support")

@router.post("/suggest", response_model=PostSuggestionsResponse, dependencies=[Depends(get_current_author)], tags=["LLM"])
def suggest_title_tags(question_data: PostSuggestionsRequest, current_user: CurrentUser, post_service: PostService = Depends()):
    """
    ## Suggests a title and tags for a post.

    This route takes a JSON body that contains the content of the post.

    ### Request Body:
    - **content** (`str`): The content of the post.

    ### Response Body:
    - **title** (`str`): The suggested title for the post.
    - **tags** (`List[str]`): The suggested tags for the post.
    """
    try:
        return post_service.suggest_title_tags(content=question_data.content)
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to suggest post title and tags, please try again later or contact support")
    