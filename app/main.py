from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host = "localhost"
        user = "root"
        password = "" # Here password
        database = "takeout_db"
    )

# Usuário
@app.route('/usuarios/criar', methods = ['POST'])
def criar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    cargo = data.get('cargo')

    con = get_db_connection()
    cursor = con.cursor()
    
    query = 'INSERT INTO Usuario (nome, email, senha, cargo) VALUES (%s %s %s %s)'
    cursor.execute(query, (nome, email, senha, cargo))
    con.commit()
    con.close()
    return jsonify({'message': f'Usuário {nome} criado com sucesso!'}), 201

@app.route('/usuarios/login', methods = ['POST'])
def login_usuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    con = get_db_connection()
    cursor = con.cursor()

    query = 'SELECT id, nome, role FROM Usuario WHERER email = %s AND senha = %s'
    cursor.execute(query,(email, senha))
    usuario = cursor.fetchone()
    con.close()

    if usuario:
        return jsonify({'message': 'Login bem-sucedido!', 'usuario':{'id': usuario[0], 'nome': usuario[1], 'cargo': usuario[2]}}), 200
    else:
        return jsonify({'message': 'Credenciais Inválidas.'}), 401
    
# Item Cardapio
