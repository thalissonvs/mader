from fastapi import FastAPI

from mader.routers import auth, romancists, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(romancists.router)


@app.get('/')
async def read_root():
    return {'message': 'Hello World!'}
