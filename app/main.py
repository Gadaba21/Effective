from openpyxl.styles.builtins import title
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from app.utils.app_factory import AppFactory
from app.utils.config import get_app_settings

app = AppFactory.make(app_settings=get_app_settings())
Instrumentator().instrument(app).expose(app)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='localhost', port=8000, reload=True)
