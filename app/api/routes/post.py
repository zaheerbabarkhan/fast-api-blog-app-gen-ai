import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_author, CurrentUser
from app.schemas.post import PostCreate, PostResponse
from app.crud import post as post_crud
router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/",dependencies=[Depends(get_current_author)], status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(db: SessionDep, author : CurrentUser, post_data: PostCreate):
    return post_crud.create_post(db=db, author=author, post_data=post_data)


@router.get("/{post_id}", response_model=PostResponse)
def read_post(db: SessionDep, post_id: str):
    try:
        post_id = uuid.UUID(str(post_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post not found")
    
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post