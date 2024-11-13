import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from datetime import datetime

load_dotenv()
DB_URL = os.getenv("DB_URL")
usuarios_bp = Blueprint("usuarios_bp", __name__)
mensajes_bp = Blueprint("mensajes_bp", __name__)

client = pymongo.MongoClient(DB_URL)
db = client.instant
usuarios = db.usuarios
contactos = db.contactos
mensajes = db.mensajes


#GET /usuarios/

@usuarios_bp.route("/", methods = ['GET'])
def get_usuarios():
    try:
        alias = request.args.get("alias")
        query = {}
    except Exception as e:
        return jsonify({"error": "Error al leer parámetros de consulta"}), 400
    
    try:
        if alias:
            query["nombre"] = {"$regex": alias, "$options": "i"}
    except Exception as e:
        return jsonify({"error": f"Error al convertir los ID: {str(e)}"}), 400
    try: 
        print("GET ALL USUARIOS")
        resultado = usuarios.find(query)
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /usuarios/<id>

@usuarios_bp.route("/<id>", methods = ["GET"])
def get_usuarios_by_id(id):
    try:
        resultado = usuarios.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de usuario por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el mensaje con id {id}")
        return jsonify({"error":"Mensaje con id especificado no encontrada"}), 404

#POST /usuarios/

@usuarios_bp.route("/", methods = ['POST'])
def create_usuario():
    datos = request.json

    if not datos or not datos["telefono"] or not datos["alias"]:
        print("Error: Parametros de entrada inválidos")

    telefono = datos["telefono"]
    alias = datos["alias"]
    usuario_existente = usuarios.find_one({"telefono":telefono})

    if usuario_existente:
        return jsonify({"error": f"Usuario con telefono {telefono} ya existe"}), 404
    else:
        usuarios.insert_one(datos)
        return jsonify({"response": f"Usuario con telefono {telefono} y alias {alias} creado correctamente"}), 201

#PUT /usuarios/<id>

@usuarios_bp.route("/<id>", methods=["PUT"])
def update_usuario(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = usuarios.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar el usuario con id {id}"}), 404
    else:
        alias = respuesta["alias"]
        return jsonify({"response":f"Usuario con alias {alias} actualizado correctamente"}), 200

#DELETE /usuarios/<id>

@usuarios_bp.route("/<id>", methods=['DELETE'])
def delete_usuario(id):

    try:
        usuario = usuarios.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = usuarios.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar el usuario con id {id}", 400
    if borrado.deleted_count == 0:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar", 200

    return "El usuario ha sido borrado con exito", 200

#CRUD DE LOS CONTACTOS DEL USUARIO

#GET /usuarios/<id>/contactos

@usuarios_bp.route("/<id>/contactos", methods = ['GET'])
def get_contactos(id):
    try: 
        print(f"GET ALL CONTACTOS FROM {id}")
        resultado = contactos.find({"idLista":id})
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /usuarios/<id>/contactos/<idContacto>

@usuarios_bp.route("/<id>/contactos/<idContacto>", methods = ["GET"])
def get_contactos_by_id(id, idContacto):
    try:
        print(f"GET {idContacto} FROM {id}")
        listaDeContactos = contactos.find({"_id":ObjectId(idContacto),"idLista":id})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if listaDeContactos:
        print("Busqueda de usuario por id")

        resultado_json = json.loads(json_util.dumps(listaDeContactos))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el contacto con id {id}")
        return jsonify({"error":"Contacto con id especificado no encontrada"}), 404

#POST /usuarios/

@usuarios_bp.route("/<id>/contactos", methods = ['POST'])
def create_contacto(id):
    datos = request.json

    if not datos or not datos["telefono"] or not datos["alias"]:
        print("Error: Parametros de entrada inválidos")

    datos["idLista"] = id

    telefono = datos["telefono"]
    alias = datos["alias"]
    
    # usuario_existente = usuarios.find_one({"telefono":telefono})
    # if usuario_existente:
    #     return jsonify({"error": f"Usuario con telefono {telefono} ya existe"}), 404
    # else:
    #     usuarios.insert_one(datos)
    #     return jsonify({"response": f"Usuario con telefono {telefono} y alias {alias} creado correctamente"}), 201

    contactos.insert_one(datos)
    return jsonify({"response":"Contacto insertado correctamente"}), 200


#PUT /usuarios/<id>

@usuarios_bp.route("/<id>/contactos/<idContacto>", methods=["PUT"])
def update_contacto(id,idContacto):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = contactos.find_one_and_update({"_id":ObjectId(idContacto)}, dataFormateada, return_document=True)
    print(respuesta)
    alias = respuesta["alias"]

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar el contacto con id {idContacto}"}), 404
    else:
        return jsonify({"response":f"Usuario con alias {alias} actualizado correctamente"}), 200

#DELETE /usuarios/<id>

@usuarios_bp.route("/<id>/contactos/<idContacto>", methods=['DELETE'])
def delete_contacto(id, idContacto):
    try:
        contacto = contactos.find_one({"_id":ObjectId(idContacto),"idLista":id})
    except Exception as e:
        return f"El contacto {idContacto} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = contactos.delete_one({"_id":ObjectId(idContacto)})
    except Exception as e:
        return f"Error al borrar el contacto con id {idContacto}", 400
    if borrado.deleted_count == 0:
        return f"El contacto {idContacto} no existe, por lo tanto no se puede borrar", 200

    return "El contacto ha sido borrado con exito", 200

#GET /usuarios/<alias>/contactos
@usuarios_bp.route("/contactos/<alias>", methods=['GET'])
def get_contactos_by_alias(alias):
    try:
        print(f"GET CONTACTOS FROM {alias}")
        listaDeContactos = contactos.find({"aliasLista":str(alias)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if listaDeContactos:
        print("Busqueda contactos por alias")

        resultado_json = json.loads(json_util.dumps(listaDeContactos))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el contacto con alias {alias}")
        return jsonify({"error":"Contacto con id especificado no encontrada"}), 404



#CRUD DE LOS MENSAJES

#GET /mensaje

@mensajes_bp.route("/", methods = ['GET'])
def get_mensajes():
    try: 
        print("GET ALL MENSAJES")
        resultado = mensajes.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /mensaje/<id>

@mensajes_bp.route("/<id>", methods = ["GET"])
def get_mensajes_by_id(id):
    try:
        resultado = mensajes.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de mensaje por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el mensaje con id {id}")
        return jsonify({"error":"Mensaje con id especificado no encontrada"}), 404

#POST /mensaje/

@mensajes_bp.route("/", methods = ['POST'])
def create_mensaje():
    datos = request.json

    if not datos or not datos["identificador"] or not datos["origen"] or not datos["destino"] or not datos["texto"]:
        print("Error: Parametros de entrada inválidos")

    datos["timestamp"] = datetime.now()

    identificador = datos["identificador"]

    mensajes.insert_one(datos)
    
    return jsonify({"response": f"Mensaje con id {identificador} ha sido creado correctamente"}), 201

    # usuario_existente = usuarios.find_one({"telefono":telefono})

    # if usuario_existente:
    #     return jsonify({"error": f"Usuario con telefono {telefono} ya existe"}), 404
    # else:
    #     usuarios.insert_one(datos)
    #     return jsonify({"response": f"Usuario con telefono {telefono} y alias {alias} creado correctamente"}), 201

#PUT /mensaje/<id>

@mensajes_bp.route("/<id>", methods=["PUT"])
def update_usuario(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = mensajes.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)
    identificador = respuesta["identificador"]

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar el mensaje con id {identificador}"}), 404
    else:
        return jsonify({"response":f"Mensaje con identificador {identificador} actualizado correctamente"}), 200

#DELETE /mensaje/<id>

@mensajes_bp.route("/<id>", methods=['DELETE'])
def delete_usuario(id):

    try:
        mensaje = mensajes.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404
    try:
        borrado = mensajes.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar el mensaje con id {id}", 400
    if borrado.deleted_count == 0:
        return f"El mensaje con id {id} no existe, por lo tanto no se puede borrar", 200

    return "El usuario ha sido borrado con exito", 200



# #GET /wikis/<id>/entradas

# @mensajes_bp.route("/<id>/entradas", methods=['GET'])
# def get_entradas_byWiki(id):
#     nombreServicio= os.getenv("ENDPOINT_ENTRADAS")
#     puertoServicio= os.getenv("SERVICE_ENTRADAS_PORT")
#     if current_app.debug:
#         url = f"http://localhost:{puertoServicio}/entradas/?idWiki={id}"
#     else:
#         url = f"http://{nombreServicio}:{puertoServicio}/entradas/?idWiki={id}"
#     resultado = requests.get(url)
#     if resultado.status_code != 200:
#         return jsonify({"error":"No se ha podido solicitar las entradas de la wiki"}), 404
#     else:
#         return jsonify(resultado.json())

