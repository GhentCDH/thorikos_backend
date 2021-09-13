import elasticsearch
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import pydantic
from starlette.requests import Request

from config import ALLOWED_ORIGINS, ELASTICSEARCH

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.es = elasticsearch.AsyncElasticsearch(hosts=ELASTICSEARCH['hosts'])

@app.on_event("shutdown")
async def shutdown():
    await app.state.es.close()

class ElasticSearchBody(pydantic.BaseModel):
    aggs: dict = None
    from_: int = None
    size: int = None
    query: dict = None

    class Config:
        fields = {
            # from is a python keyword
            'from_': 'from',
        }

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        # from is a python keyword
        d['from'] = d.pop('from_')
        # don't return items with value None
        return {k: v for (k, v) in d.items() if v is not None}

@app.post('/search')
async def search(
    es_body: ElasticSearchBody,
    request: Request
):
    return await request.app.state.es.search(
        index=ELASTICSEARCH['indexname'],
        body=es_body.dict()
    )

@app.get('/{entity_type}/{entity_id}')
async def doc(
    entity_type: str,
    entity_id: str,
    request: Request
):
    return await request.app.state.es.get(
        index=ELASTICSEARCH['indexname'],
        id=f'{entity_type}__{entity_id}'
    )
