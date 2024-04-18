from fastapi.templating import Jinja2Templates
from fastapi.routing import APIRouter
from fastapi.requests import Request
from starlette.responses import FileResponse

router = APIRouter(
    prefix="/idk",
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")


@router.get('/register')
async def registration(request: Request):
    # return templates.TemplateResponse("/auth/register.html", context={"request": request})
    return FileResponse("templates/auth/register.html", status_code=200)


@router.get('/login')
async def registration(request: Request):
    # return templates.TemplateResponse("/auth/register.html", context={"request": request})
    return FileResponse("templates/auth/login.html", status_code=200)
