from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from neatsheets.sheet import Sheet, Language, Platform

root = Path(__file__).parent

app = FastAPI()
app.mount('/static', StaticFiles(directory=(root / 'static')), name='static')

templates = Jinja2Templates(directory=(root / 'templates'),
                            loader=FileSystemLoader((root / 'templates'), encoding='UTF-16BE'))


@app.get("/{language}/sheet/{application}", response_class=HTMLResponse)
@app.get("/{language}/sheet/{application}.html", response_class=HTMLResponse)
async def sheet(request: Request, language: Language, application: str, platform: Platform = Platform.MAC):
    """ Render Neatsheet """
    sheet = Sheet.build_sheet(language, application, platform)
    return templates.TemplateResponse('sheet.html', {
        'request': request, 'application': application, 'platform': platform, 'sheet': sheet})


def main():
    """ Run webserver """
    uvicorn.run(app, host='localhost', port=8000, debug=True)


if __name__ == '__main__':
    main()
