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
    params = {
        "idsTiposComb": 3201,
        "qtdPorPagina": 50,
        "pagina": 1
    }

    response = requests.get(url, params=params)
    data = response.json().get("resultado", [])

    postos_formatados = []
    for posto in data:
        try:
            preco_float = float(posto["Preco"].replace(",", ".").split()[0])
            postos_formatados.append({
                "Posto": posto["Nome"].strip(),
                "Marca": posto["Marca"].strip(),
                "Preço (€)": f"{preco_float:.3f}",
                "Localidade": posto["Morada"].strip().replace("\r", " ")
            })
        except:
            continue

    postos_ordenados = sorted(postos_formatados, key=lambda x: float(x["Preço (€)"]))

    return templates.TemplateResponse("barato.html", {
        "request": request,
        "postos": postos_ordenados[:5]
    })
