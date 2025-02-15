from flask import Flask, jsonify, request, render_template, send_from_directory
import json
import os
from PIL import Image

app = Flask(__name__)

# Configuración básica
app.config['DEBUG'] = True

# Asegurarnos de que existe la carpeta static
if not os.path.exists('static'):
    os.makedirs('static')

# Crear un favicon básico si no existe
if not os.path.exists('static/favicon.ico'):
    img = Image.new('RGB', (16, 16), color = '#1a237e')
    img.save('static/favicon.ico')

# Cargar datos desde el archivo JSON
with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Ruta para obtener todas las enfermedades
@app.route("/api/enfermedades", methods=["GET"])
def obtener_enfermedades():
    return jsonify(data)

# Ruta para buscar una enfermedad por nombre
@app.route("/api/enfermedades/<nombre>", methods=["GET"])
def buscar_enfermedad(nombre):
    enfermedad = next((e for e in data if e["nombre"].lower() == nombre.lower()), None)
    return jsonify(enfermedad) if enfermedad else jsonify({"error": "No encontrada"}), 404

@app.route("/api/buscar-sintoma", methods=["GET"])
def buscar_por_sintoma():
    sintoma = request.args.get('sintoma', '').lower().strip()
    if not sintoma:
        return jsonify({"error": "Debe proporcionar un síntoma"}), 400
    
    # Dividir la búsqueda en palabras para búsqueda más flexible
    palabras_busqueda = sintoma.split()
    
    enfermedades_encontradas = []
    for enfermedad in data:
        encontrado = False
        # Convertir todos los síntomas a minúsculas para comparación
        for sintoma_enfermedad in enfermedad["sintomas"]:
            sintoma_lower = sintoma_enfermedad.lower()
            # Buscar coincidencias exactas primero
            if sintoma in sintoma_lower:
                encontrado = True
                break
            # Si no hay coincidencia exacta, buscar palabras individuales
            for palabra in palabras_busqueda:
                if palabra in sintoma_lower:
                    encontrado = True
                    break
            if encontrado:
                break
        
        if encontrado:
            enfermedades_encontradas.append(enfermedad)
    
    # Ordenar resultados por relevancia (coincidencia exacta primero)
    enfermedades_encontradas.sort(
        key=lambda e: any(sintoma in s.lower() for s in e["sintomas"]),
        reverse=True
    )
    
    return jsonify(enfermedades_encontradas)

@app.route("/api/sintomas", methods=["GET"])
def obtener_sintomas():
    # Obtener lista única de todos los síntomas
    todos_sintomas = set()
    for enfermedad in data:
        todos_sintomas.update(enfermedad["sintomas"])
    return jsonify(sorted(list(todos_sintomas)))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    try:
        print("Iniciando servidor...")
        app.run(host='localhost', port=5001)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
