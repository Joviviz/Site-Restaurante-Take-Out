from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="takeout_db"
    )

# ----------------- USUÁRIO ----------------- #
@app.route('/usuarios/criar', methods=['POST'])
def criar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    role = data.get('role')

    con = get_db_connection()
    cursor = con.cursor()
    query = 'INSERT INTO Usuario (nome, email, senha, role) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (nome, email, senha, role))
    con.commit()
    con.close()
    return jsonify({'message': f'Usuário {nome} criado com sucesso!'}), 201

@app.route('/usuarios/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    con = get_db_connection()
    cursor = con.cursor()
    query = 'SELECT id, nome, role FROM Usuario WHERE email = %s AND senha = %s'
    cursor.execute(query, (email, senha))
    usuario = cursor.fetchone()
    con.close()

    if usuario:
        return jsonify({'message': 'Login bem-sucedido!', 'usuario': {'id': usuario[0], 'nome': usuario[1], 'role': usuario[2]}}), 200
    else:
        return jsonify({'message': 'Credenciais inválidas.'}), 401

# ----------------- ITEM CARDÁPIO ----------------- #
@app.route('/cardapio/criar', methods=['POST'])
def criar_item():
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    usuario_id = data.get('usuario_id')

    con = get_db_connection()
    cursor = con.cursor()
    query = 'INSERT INTO ItemCardapio (nome, descricao, preco, usuario_id) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (nome, descricao, preco, usuario_id))
    con.commit()
    con.close()
    return jsonify({'message': 'Item de cardápio criado com sucesso!'}), 201

@app.route('/cardapio', methods=['GET'])
def listar_cardapio():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('SELECT id, nome, descricao, preco, disponivel FROM ItemCardapio')
    itens = cursor.fetchall()
    con.close()
    return jsonify(itens), 200

# ----------------- CARRINHO ----------------- #
@app.route('/carrinho/adicionar', methods=['POST'])
def adicionar_carrinho():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    item_id = data.get('item_id')
    quantidade = data.get('quantidade', 1)

    con = get_db_connection()
    cursor = con.cursor()
    query = 'INSERT INTO Carrinho (usuario_id, item_id, quantidade) VALUES (%s, %s, %s)'
    cursor.execute(query, (usuario_id, item_id, quantidade))
    con.commit()
    con.close()
    return jsonify({'message': 'Item adicionado ao carrinho!'}), 201

@app.route('/carrinho/<int:usuario_id>', methods=['GET'])
def listar_carrinho(usuario_id):
    con = get_db_connection()
    cursor = con.cursor()
    query = '''
        SELECT C.id, I.nome, C.quantidade, I.preco, (C.quantidade * I.preco) as subtotal
        FROM Carrinho C
        JOIN ItemCardapio I ON C.item_id = I.id
        WHERE C.usuario_id = %s
    '''
    cursor.execute(query, (usuario_id,))
    itens = cursor.fetchall()
    con.close()
    return jsonify(itens), 200

# ----------------- PEDIDO ----------------- #
@app.route('/pedido/criar', methods=['POST'])
def criar_pedido():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    item_id = data.get('item_id')
    quantidade = data.get('quantidade', 1)
    valor_total = data.get('valorTotal')
    status = data.get('status', 'PENDENTE')

    con = get_db_connection()
    cursor = con.cursor()
    query = '''
        INSERT INTO Pedido (status, valorTotal, usuario_id, item_id, quantidade)
        VALUES (%s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (status, valor_total, usuario_id, item_id, quantidade))
    con.commit()
    con.close()
    return jsonify({'message': 'Pedido realizado com sucesso!'}), 201

@app.route('/pedido/<int:usuario_id>', methods=['GET'])
def listar_pedidos(usuario_id):
    con = get_db_connection()
    cursor = con.cursor()
    query = '''
        SELECT P.id, I.nome, P.quantidade, P.valorTotal, P.status
        FROM Pedido P
        JOIN ItemCardapio I ON P.item_id = I.id
        WHERE P.usuario_id = %s
    '''
    cursor.execute(query, (usuario_id,))
    pedidos = cursor.fetchall()
    con.close()
    return jsonify(pedidos), 200

# ----------------- PAGAMENTO ----------------- #
@app.route('/pagamento/registrar', methods=['POST'])
def registrar_pagamento():
    data = request.get_json()
    metodo = data.get('metodo')
    valor = data.get('valor')
    status = data.get('status')
    pedido_id = data.get('pedido_id')

    con = get_db_connection()
    cursor = con.cursor()
    query = 'INSERT INTO Pagamento (metodo, valor, status, pedido_id) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (metodo, valor, status, pedido_id))
    con.commit()
    con.close()
    return jsonify({'message': 'Pagamento registrado com sucesso!'}), 201

@app.route('/pagamento/<int:pedido_id>', methods=['GET'])
def obter_pagamento(pedido_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('SELECT metodo, valor, status FROM Pagamento WHERE pedido_id = %s', (pedido_id,))
    pagamento = cursor.fetchone()
    con.close()

    if pagamento:
        return jsonify({'metodo': pagamento[0], 'valor': pagamento[1], 'status': pagamento[2]}), 200
    else:
        return jsonify({'message': 'Pagamento não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)