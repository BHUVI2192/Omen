import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
app = FastAPI(title='OMEN API', version='1.0.0', description='Institutional career intelligence and employability platform')
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',') if x.strip()], allow_credentials=True, allow_methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS'], allow_headers=['Authorization','Content-Type','Accept'])
app.include_router(router, prefix='/api/v1')

@app.get('/')
def root(): return {'name':'OMEN','message':'Your career should not be a guess.','docs':'/docs'}
