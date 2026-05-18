# Hackathon Banamex
## Eduardo Porto Morales, Sergio Jiawei Xuan, Valentina González, Rodrigo Sosa, Gabriel Muñoz, Hector Julián Zárate

## 📖 Descripción
> En este proyecto, realizamos un análisis de sentimiento en las muchas sucursales de Banamex. Al utilizar modelos de IA, pudimos clasificar todas las verbalizaciones, encontrar patrones y mostrar a través de graficas los niveles de satisfaccion de todas las sucursales.

---

## 🚀 Características
- Análisis de Sentimiento
- Clasificación de verbalizaciones usando modelos de IA
- Panel de graficas
- Interfaz responsiva

---

## 📦 Dependencias

### Dependencias principales

| Dependencia | Descripción |
|---|---|
| React | Librería para la interfaz de usuario |
| Vite | Herramienta de desarrollo y build |
| FastAPI | Servidor backend |

> Debido a nuestro compromiso por la confidencialidad, los datos no pueden ser almacenados en este repositorio.

---

## ⚙️ Instalación

```bash
# Clonar repositorio
git clone <repo-url>

# Entrar al proyecto
cd Hackathon_Banamex

# Instalar dependencias
npm install

#Entrar y correr el Backend

cd NLP

uvicorn main:app --reload

#En una segunda terminal sin cerrar donde corre el Backend, para correr el Frontend

cd Frontend/src
pnpm run dev
