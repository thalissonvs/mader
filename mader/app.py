from fastapi import FastAPI

from mader.routers import auth, books, romancists, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(romancists.router)
app.include_router(books.router)


@app.get('/')
async def read_root():
    return {'message': 'Hello World!'}
