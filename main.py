from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests


app = FastAPI()
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home():
    return {"message": "Vai para /barato para veres o site"}

@app.get("/barato", response_class=HTMLResponse)
def mais_barato(request: Request):
    url = "https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/PesquisarPostos"
    params = {"idsTiposComb": 3201, "qtdPorPagina": 50, "pagina": 1}

    resp = requests.get(url, params=params, verify=False)
    data = resp.json().get("resultado", [])

    postos = []
    for p in data:
        try:
            preco = float(p["Preco"].replace(",", ".").split()[0])
            postos.append({
                "Posto":       p["Nome"].strip(),
                "Marca":       p["Marca"].strip(),
                "Preco":       f"{preco:.3f}",
                "Localidade":  p["Morada"].strip().replace("\r"," "),
                "Lat":         round(p["Latitude"], 6),
                "Lng":         round(p["Longitude"], 6),
            })
        except:
            continue

    postos = sorted(postos, key=lambda x: float(x["Preco"]))[:5]
    return templates.TemplateResponse("barato.html", {
        "request": request,
        "postos":  postos
    })
