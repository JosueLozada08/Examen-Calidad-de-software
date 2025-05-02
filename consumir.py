import requests
from datetime import datetime
import pandas as pd

class ClienteAPI:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def cargar_csv(self, archivo_csv):
        """Carga un archivo CSV a través del endpoint /cargar_csv/"""
        try:
            with open(archivo_csv, 'rb') as f:
                files = {'file': (archivo_csv, f, 'text/csv')}
                response = self.session.post(f"{self.base_url}/cargar_csv/", files=files)
                response.raise_for_status()
                resultado = response.json()
                print(f"✅ {resultado['mensaje']}")
        except Exception as e:
            print(f"❌ Error al cargar CSV: {str(e)}")

    def buscar_cliente(self, cliente_id):
        """Busca un cliente por ID"""
        try:
            response = self.session.get(f"{self.base_url}/cliente/{cliente_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("❌ No se encontró un cliente con ese ID.")
            else:
                print(f"❌ Error en la solicitud: {str(e)}")
            return None

    def listar_por_ciudad(self, ciudad):
        """Lista clientes por ciudad (case-insensitive) y ordena por apellidos"""
        try:
            response = self.session.get(f"{self.base_url}/clientes/ciudad/{ciudad}")
            response.raise_for_status()
            data = response.json()
            if not data:
                print("❌ No se encontraron clientes en la ciudad especificada.")
                return None
            df = pd.DataFrame(data)
            df = df[['nombres', 'apellidos', 'ciudad', 'email']]
            df.sort_values(by='apellidos', inplace=True)
            return df
        except Exception as e:
            print(f"❌ Error al listar por ciudad: {str(e)}")
            return None

    def listar_por_edad(self, edad, condicion):
        """Lista clientes mayores o menores que una edad dada, ordenados de mayor a menor edad"""
        try:
            response = self.session.get(f"{self.base_url}/clientes")
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data)

            if condicion == "mayores":
                df = df[df["edad"] > edad].sort_values(by="edad", ascending=False)
            elif condicion == "menores":
                df = df[df["edad"] < edad].sort_values(by="edad", ascending=False)
            else:
                print("❌ Condición inválida. Use 'mayores' o 'menores'.")
                return None

            if df.empty:
                print("❌ No se encontraron clientes que cumplan con la condición.")
                return None

            return df[["id", "nombres", "edad", "email"]]
        except Exception as e:
            print(f"❌ Error al filtrar por edad: {str(e)}")
            return None


    def listar_todos(self):
        """Obtiene todos los clientes"""
        try:
            response = self.session.get(f"{self.base_url}/clientes")
            response.raise_for_status()
            return pd.DataFrame(response.json())
        except Exception as e:
            print(f"❌ Error al obtener todos los clientes: {str(e)}")
            return None

    def mostrar_resultados(self, df):
        """Muestra resultados en formato tabla"""
        if df is None or df.empty:
            print("⚠️ No se encontraron resultados.")
        else:
            print(df.to_markdown(index=False, tablefmt="grid"))


# Menú interactivo
def menu_interactivo():
    cliente_api = ClienteAPI()

    while True:
        print("\n=== MENÚ API CLIENTES ===")
        print("1. Cargar archivo CSV")
        print("2. Buscar cliente por ID")
        print("3. Listar clientes por ciudad")
        print("4. Listar clientes por edad (mayores/menores)")
        print("5. Mostrar todos los clientes")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "0":
            break
        elif opcion == "1":
            archivo = input("Ruta del archivo CSV: ")
            cliente_api.cargar_csv(archivo)
        elif opcion == "2":
            cliente_id = input("ID del cliente: ")
            if cliente_id.isdigit():
                resultado = cliente_api.buscar_cliente(int(cliente_id))
                cliente_api.mostrar_resultados(pd.DataFrame([resultado]) if resultado else None)
            else:
                print("❌ El ID debe ser un número entero.")
        elif opcion == "3":
            ciudad = input("Ciudad a buscar: ")
            resultados = cliente_api.listar_por_ciudad(ciudad)
            cliente_api.mostrar_resultados(resultados)
        elif opcion == "4":
            condicion = input("¿Desea ver clientes 'mayores' o 'menores' que cierta edad?: ").strip().lower()
            edad = input("Edad: ")
            if edad.isdigit() and condicion in ["mayores", "menores"]:
                resultados = cliente_api.listar_por_edad(int(edad), condicion)
                cliente_api.mostrar_resultados(resultados)
            else:
                print("❌ Entrada inválida. Intente nuevamente.")
        elif opcion == "5":
            resultados = cliente_api.listar_todos()
            cliente_api.mostrar_resultados(resultados)
        else:
            print("⚠️ Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    menu_interactivo()
