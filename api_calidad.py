from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime, date
import pandas as pd
import io

# Inicializar aplicación FastAPI
app = FastAPI()

# Variable global para almacenar el DataFrame
clientes_df = pd.DataFrame()

# Modelo para representar un cliente
class Cliente(BaseModel):
    id: int
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    ciudad: str
    fecha_registro: date
    email: str
    edad: int

# Función para calcular la edad desde la fecha de nacimiento
def calcular_edad(fecha_nac):
    today = date.today()
    return today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))

# Cargar CSV con datos de clientes
@app.post("/cargar_csv/")
async def cargar_csv(file: UploadFile = File(...)):
    global clientes_df
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        columnas_esperadas = ['id', 'nombres', 'apellidos', 'fecha_nacimiento', 'ciudad', 'fecha_registro', 'email']
        if not all(col in df.columns for col in columnas_esperadas):
            raise HTTPException(status_code=400, detail="CSV no tiene todas las columnas requeridas.")

        # Convertir fechas y calcular edad
        df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento'], errors='coerce')
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], errors='coerce')
        df['edad'] = df['fecha_nacimiento'].apply(lambda x: calcular_edad(x) if pd.notnull(x) else None)

        # Eliminar registros con campos inválidos
        clientes_df = df.dropna(subset=columnas_esperadas)

        return {"mensaje": f"{len(clientes_df)} registros válidos cargados correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

# Buscar cliente por ID
@app.get("/cliente/{cliente_id}", response_model=Cliente)
def buscar_cliente(cliente_id: int):
    global clientes_df
    cliente = clientes_df[clientes_df['id'] == cliente_id]
    if cliente.empty:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return cliente.iloc[0].to_dict()

# Listar clientes por ciudad
@app.get("/clientes/ciudad/{nombre_ciudad}", response_model=List[Cliente])
def listar_por_ciudad(nombre_ciudad: str):
    global clientes_df
    clientes = clientes_df[clientes_df['ciudad'].str.lower() == nombre_ciudad.lower()]
    return clientes.to_dict(orient='records')

# Listar clientes por rango de edad
@app.get("/clientes/edad/", response_model=List[Cliente])
def listar_por_edad(min_edad: int, max_edad: int):
    global clientes_df
    clientes = clientes_df[(clientes_df['edad'] >= min_edad) & (clientes_df['edad'] <= max_edad)]
    return clientes.to_dict(orient='records')

# Ver todos los clientes
@app.get("/clientes", response_model=List[Cliente])
def listar_todos():
    global clientes_df
    return clientes_df.to_dict(orient='records')
