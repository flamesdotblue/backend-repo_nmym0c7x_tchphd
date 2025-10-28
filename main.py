import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import BlogPost

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------- Blog Posts Endpoints ----------
class BlogPostOut(BaseModel):
    id: str
    title: str
    content: str
    author: str
    tags: Optional[list[str]] = None
    created_at: Optional[str] = None


def serialize_post(doc: dict) -> BlogPostOut:
    return BlogPostOut(
        id=str(doc.get("_id")),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        author=doc.get("author", ""),
        tags=doc.get("tags"),
        created_at=str(doc.get("created_at")) if doc.get("created_at") else None,
    )


@app.get("/posts", response_model=List[BlogPostOut])
async def list_posts(limit: int = 50):
    try:
        docs = get_documents("blogpost", {}, limit)
        posts = [serialize_post(d) for d in docs]
        # newest first by created_at if available
        posts.sort(key=lambda p: p.created_at or "", reverse=True)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts", response_model=dict)
async def create_post(post: BlogPost):
    try:
        new_id = create_document("blogpost", post)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}", response_model=BlogPostOut)
async def get_post(post_id: str):
    try:
        # validate ObjectId
        try:
            oid = ObjectId(post_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid post id")
        res = db["blogpost"].find_one({"_id": oid})
        if not res:
            raise HTTPException(status_code=404, detail="Post not found")
        return serialize_post(res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
