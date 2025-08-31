# FastAPI 애플리케이션 생성 및 서버 실행
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid

# FastAPI 인스턴스 생성
app = FastAPI(
    title="Book Management API",
    description="A simple API for managing a collection of books.",
    version="1.0.0"
)

# In-memory 데이터베이스 (실제로는 DB를 사용)
books_db: Dict[uuid.UUID, dict] = {}

# Pydantic을 이용한 Book 모델 정의
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=2, max_length=50)
    year: int = Field(..., gt=1000, lt=2100)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=2, max_length=50)
    year: Optional[int] = Field(None, gt=1000, lt=2100)

class BookInDB(BookBase):
    id: uuid.UUID

# 1. 모든 도서 목록 조회
@app.get("/books/", response_model=List[BookInDB])
async def get_all_books(
    skip: int = Query(0, description="Number of items to skip."),
    limit: int = Query(10, description="Maximum number of items to return.")
):
    """모든 도서 목록을 반환합니다."""
    books = list(books_db.values())
    return [BookInDB(**book) for book in books[skip : skip + limit]]

# 2. 특정 도서 조회
@app.get("/books/{book_id}", response_model=BookInDB)
async def get_book(
    book_id: uuid.UUID = Path(..., description="The ID of the book to retrieve.")
):
    """ID로 특정 도서를 조회합니다."""
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ID {book_id} not found."
        )
    return BookInDB(**books_db[book_id])

# 3. 새로운 도서 생성
@app.post("/books/", response_model=BookInDB, status_code=201)
async def create_book(book: BookCreate):
    """새로운 도서를 생성합니다."""
    book_id = uuid.uuid4()
    new_book = book.dict()
    new_book["id"] = book_id
    books_db[book_id] = new_book
    return BookInDB(**new_book)

# 4. 도서 정보 수정
@app.put("/books/{book_id}", response_model=BookInDB)
async def update_book(
    book_id: uuid.UUID = Path(..., description="The ID of the book to update."),
    book: BookUpdate = ...
):
    """ID로 도서 정보를 업데이트합니다."""
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ID {book_id} not found."
        )
    
    current_book = books_db[book_id]
    update_data = book.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        current_book[key] = value

    books_db[book_id] = current_book
    return BookInDB(**current_book)

# 5. 도서 삭제
@app.delete("/books/{book_id}", status_code=204)
async def delete_book(
    book_id: uuid.UUID = Path(..., description="The ID of the book to delete.")
):
    """ID로 특정 도서를 삭제합니다."""
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ID {book_id} not found."
        )
    
    del books_db[book_id]

# 6. 도서 검색 (제목, 저자, 출판 연도)
@app.get("/search/", response_model=List[BookInDB])
async def search_books(
    q: Optional[str] = Query(None, description="Search term for title or author."),
    year: Optional[int] = Query(None, description="Filter by publication year.")
):
    """도서를 제목, 저자, 또는 출판 연도로 검색합니다."""
    filtered_books = []
    
    for book_data in books_db.values():
        match = True
        
        if q:
            if q.lower() not in book_data["title"].lower() and \
               q.lower() not in book_data["author"].lower():
                match = False
        
        if year is not None:
            if book_data["year"] != year:
                match = False
        
        if match:
            filtered_books.append(BookInDB(**book_data))
            
    return filtered_books

# 서버 실행 (터미널에서 'uvicorn main:app --reload' 실행)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)