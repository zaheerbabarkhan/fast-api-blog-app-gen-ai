import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.deps import SessionDep, get_current_admin, get_current_author, CurrentUser, get_current_user
from app.models.user import UserRole
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate
from app.schemas.comment import CommentCreateRequest, CommentResponse, CommentResponseWithReplies
from app.crud import post as post_crud
from app.crud import comment as comment_crud


router = APIRouter(prefix="/posts")

@router.post("/",dependencies=[Depends(get_current_author)], status_code=status.HTTP_201_CREATED, response_model=PostResponse, tags=["Author"])
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


@router.get("/{post_id}", response_model=PostResponse, tags=["Post"])
def get_post(db: SessionDep, post_id: str):
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

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return post


@router.put("/{post_id}", response_model=PostResponse, dependencies=[Depends(get_current_author)], tags=["Author"])
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


@router.get("/", response_model=List[PostListResponse], tags=["Post"])
def get_posts(db: SessionDep):

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


@router.post("/{post_id}/comments", response_model=CommentResponse, tags=["Comment"])
def create_comment(db: SessionDep, post_id: str, comment_data: CommentCreateRequest, current_user: CurrentUser):
    """
    ## Creates a new comment on a post.

    This route takes a path parameter that is the post ID and a JSON body that contains the comment data.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to comment on.

    ### Request Body:
    - **content** (`str`): The content of the comment.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.

    ### Response:
    - **id** (`uuid.UUID`): The ID of the comment.
    - **content** (`str`): The content of the comment.
    - **post_id** (`uuid.UUID`): The ID of the post the comment belongs to.
    - **author_id** (`uuid.UUID`): The ID of the author of the comment.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return comment_crud.create_comment(db=db, post_id=post_id, commenter=current_user, comment_data=comment_data)


@router.get("/{post_id}/comments", response_model=List[CommentResponseWithReplies], tags=["Comment"], dependencies=[Depends(get_current_user)])
def get_comments(db: SessionDep, post_id: str):
    """
    ## Reads all comments on a post.

    This route takes a path parameter that is the post ID.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to read comments from.

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
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return comment_crud.get_post_comments(db=db, post_id=post_id)


@router.post("/{post_id}/comments/{comment_id}/reply", response_model=CommentResponse, tags=["Comment"])
def reply_to_comment(db: SessionDep, post_id: str, comment_id: str, comment_data: CommentCreateRequest, current_user: CurrentUser):
    """
    ## Replies to a comment on a post.

    This route takes a path parameter that is the post ID, a path parameter that is the comment ID, and a JSON body that contains the reply data.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to reply to.
    - **comment_id** (`str`): The ID of the comment to reply to.

    ### Request Body:
    - **content** (`str`): The content of the reply.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.

    ### Response:
    - **id** (`uuid.UUID`): The ID of the reply.
    - **content** (`str`): The content of the reply.
    - **post_id** (`uuid.UUID`): The ID of the post the reply belongs to.
    - **comment_id** (`uuid.UUID`): The ID of the comment the reply belongs to.
    - **author_id** (`uuid.UUID`): The ID of the author of the reply.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    try:
        uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment not found")

    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    try:
        uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment not found")
    
    comment = comment_crud.get_comment(db=db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    return comment_crud.reply_to_comment(db=db, post_id=post_id, parent_comment_id=comment_id, replier=current_user, reply_data=comment_data)


@router.delete("/comments/{comment_id}", tags=["Comment"])
def delete_comment(db: SessionDep, post_id: str, comment_id: str, current_user: CurrentUser):
    """
    ## Deletes a comment on a post.

    This route takes a path parameter that is the post ID and a path parameter that is the comment ID.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to delete the comment from.
    - **comment_id** (`str`): The ID of the comment to delete.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.
    - **HTTPException**: If the user is not authorized to delete the comment.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    try:
        uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment not found")

    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    comment = comment_crud.get_comment(db=db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    if comment.commenter_id != current_user.id and current_user.user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete comment")
    
    comment_crud.delete_comment(db=db, comment=comment)

    return {"message": "Comment deleted successfully"}


@router.put("/comments/{comment_id}", response_model=CommentResponse, tags=["Comment"])
def update_comment(db: SessionDep, post_id: str, comment_id: str, comment_data: CommentCreateRequest, current_user: CurrentUser):
    """
    ## Updates a comment on a post.

    This route takes a path parameter that is the post ID, a path parameter that is the comment ID, and a JSON body that contains the updated comment data.

    ### Path Parameters:
    - **post_id** (`str`): The ID of the post to update the comment on.
    - **comment_id** (`str`): The ID of the comment to update.

    ### Request Body:
    - **content** (`str`): The updated content of the comment.

    ### Raises:
    - **HTTPException**: If the post ID is not a valid UUID.
    - **HTTPException**: If the post is not found.
    - **HTTPException**: If the comment ID is not a valid UUID.
    - **HTTPException**: If the comment is not found.
    - **HTTPException**: If the user is not authorized to update the comment.

    ### Response:
    - **id** (`uuid.UUID`): The ID of the updated comment.
    - **content** (`str`): The content of the updated comment.
    - **post_id** (`uuid.UUID`): The ID of the post the updated comment belongs to.
    - **author_id** (`uuid.UUID`): The ID of the author of the updated comment.
    """
    try:
        uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    try:
        uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment not found")

    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    comment = comment_crud.get_comment(db=db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    if comment.commenter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update comment")
    
    return comment_crud.update_comment(db=db, comment=comment, comment_data=comment_data)