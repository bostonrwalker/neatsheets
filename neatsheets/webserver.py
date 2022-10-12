from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from neatsheets.app import AppManager
from neatsheets.language import Language
from neatsheets.platform import Platform


root = Path(__file__).parent

api = FastAPI()
api.mount('/static', StaticFiles(directory=(root / 'static')), name='static')

templates = Jinja2Templates(directory=(root / 'templates'),
                            loader=FileSystemLoader((root / 'templates'), encoding='UTF-16BE'))


@api.get("/{language}/sheet/{app_name}", response_class=HTMLResponse)
@api.get("/{language}/sheet/{app_name}.html", response_class=HTMLResponse)
async def sheet(request: Request, language: Language, app_name: str, platform: Platform = Platform.Mac):
    """ Render Neatsheet """
    app = AppManager.get_instance().get_app(language, app_name)
    print(str(app.logo.relative_to(root)))
    return templates.TemplateResponse('app.html', {
        'request': request, 'root': root, 'app': app, 'selected_platform': platform})


def main():
    """ Run webserver """
    AppManager.get_instance().load_all()
    uvicorn.run(api, host='localhost', port=8000, debug=True)


if __name__ == '__main__':
    main()
