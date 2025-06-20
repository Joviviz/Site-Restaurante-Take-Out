# app.py - API Flask Atualizada
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector

app = Flask(__name__,
            static_url_path='',
            static_folder='app')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, 'index.html')

def get_db_connection():
    """
    Função para estabelecer e retornar uma conexão com o banco de dados MySQL.
    """
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="252411",
        database="takeout_db"
    )

# ----------------- USUÁRIO ----------------- #
@app.route('/usuarios/criar', methods=['POST'])
def criar_usuario():
    """
    Cria um novo usuário no banco de dados.
    Recebe nome, email, senha e cargo via JSON.
    """
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    cargo = data.get('cargo')

    if not all([nome, email, senha, cargo]):
        return jsonify({'message': 'Dados incompletos para criar usuário.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()
        query = 'INSERT INTO Usuario (nome, email, senha, cargo) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, (nome, email, senha, cargo))
        con.commit()
        return jsonify({'message': f'Usuário {nome} criado com sucesso!'}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry for unique key (e.g., email)
            return jsonify({'message': 'Este email já está registrado.'}), 409
        print(f"Erro ao criar usuário: {err}")
        return jsonify({'message': 'Erro interno ao criar usuário.'}), 500
    finally:
        if con:
            con.close()

@app.route('/usuarios/login', methods=['POST'])
def login_usuario():
    """
    Autentica um usuário e retorna seus dados básicos em caso de sucesso.
    Recebe email e senha via JSON.
    """
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not all([email, senha]):
        return jsonify({'message': 'Email e senha são obrigatórios.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()
        query = 'SELECT id, nome, cargo FROM Usuario WHERE email = %s AND senha = %s'
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()

        if usuario:
            return jsonify({'message': 'Login bem-sucedido!', 'usuario': {'id': usuario[0], 'nome': usuario[1], 'cargo': usuario[2]}}), 200
        else:
            return jsonify({'message': 'Credenciais inválidas.'}), 401
    except mysql.connector.Error as err:
        print(f"Erro ao logar usuário: {err}")
        return jsonify({'message': 'Erro interno ao logar usuário.'}), 500
    finally:
        if con:
            con.close()

# ----------------- ITEM CARDÁPIO ----------------- #
@app.route('/cardapio/criar', methods=['POST'])
def criar_item():
    """
    Cria um novo item no cardápio.
    Recebe nome, descricao, preco e usuario_id via JSON.
    """
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    usuario_id = data.get('usuario_id')
    # Nota: image_path não está na tabela, mas é bom pensar em como será adicionado futuramente.

    if not all([nome, preco, usuario_id]):
        return jsonify({'message': 'Dados incompletos para criar item do cardápio.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()
        query = 'INSERT INTO ItemCardapio (nome, descricao, preco, usuario_id) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, (nome, descricao, preco, usuario_id))
        con.commit()
        return jsonify({'message': 'Item de cardápio criado com sucesso!'}), 201
    except mysql.connector.Error as err:
        print(f"Erro ao criar item do cardápio: {err}")
        return jsonify({'message': 'Erro interno ao criar item do cardápio.'}), 500
    finally:
        if con:
            con.close()

@app.route('/cardapio', methods=['GET'])
def listar_cardapio():
    """
    Lista todos os itens disponíveis no cardápio.
    Inclui um caminho de imagem hardcoded para cada item.
    """
    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True) # Retorna linhas como dicionários
        cursor.execute('SELECT id, nome, descricao, preco, disponivel FROM ItemCardapio')
        itens = cursor.fetchall()

        # Hardcoding de caminhos de imagem.
        # Em um sistema real, você teria uma coluna 'image_path' no seu DB
        # ou faria um mapeamento mais sofisticado.
        image_paths = {
            1: '/views/static/imgs/shop1.png', # Sorvete de Baunilha
            2: '/views/static/imgs/shop2.png', # Salada de Frango
            3: '/views/static/imgs/shop3.png', # Rolinho Primavera
            4: '/views/static/imgs/shop4.png', # Cogumelos Recheados
            5: '/views/static/imgs/shop5.png', # Pão de Alho
            6: '/views/static/imgs/shop6.png', # Refogado de Legumes
        }

        # Adiciona o caminho da imagem a cada item
        for item in itens:
            item['image'] = image_paths.get(item['id'], '/views/static/imgs/placeholder.png') # Placeholder se não encontrar

        return jsonify(itens), 200
    except mysql.connector.Error as err:
        print(f"Erro ao listar cardápio: {err}")
        return jsonify({'message': 'Erro interno ao listar cardápio.'}), 500
    finally:
        if con:
            con.close()

# ----------------- CARRINHO ----------------- #
@app.route('/carrinho/adicionar', methods=['POST'])
def adicionar_ou_atualizar_carrinho():
    """
    Adiciona um item ao carrinho ou atualiza sua quantidade se já existir.
    Recebe usuario_id, item_id e quantidade via JSON.
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    item_id = data.get('item_id')
    quantidade = data.get('quantidade', 1)

    if not all([usuario_id, item_id, quantidade]):
        return jsonify({'message': 'Dados incompletos para adicionar/atualizar carrinho.'}), 400
    if quantidade <= 0:
        return jsonify({'message': 'Quantidade deve ser maior que zero para adicionar.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()

        # Verifica se o item já existe no carrinho para este usuário
        select_query = 'SELECT id, quantidade FROM Carrinho WHERE usuario_id = %s AND item_id = %s'
        cursor.execute(select_query, (usuario_id, item_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Item existe, atualiza a quantidade
            carrinho_id = existing_item[0]
            nova_quantidade = existing_item[1] + quantidade
            update_query = 'UPDATE Carrinho SET quantidade = %s WHERE id = %s'
            cursor.execute(update_query, (nova_quantidade, carrinho_id))
            con.commit()
            return jsonify({'message': f'Quantidade do item {item_id} atualizada no carrinho!'}), 200
        else:
            # Item não existe, adiciona novo
            insert_query = 'INSERT INTO Carrinho (usuario_id, item_id, quantidade) VALUES (%s, %s, %s)'
            cursor.execute(insert_query, (usuario_id, item_id, quantidade))
            con.commit()
            return jsonify({'message': 'Item adicionado ao carrinho!'}), 201
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar/atualizar carrinho: {err}")
        return jsonify({'message': 'Erro interno ao adicionar/atualizar carrinho.'}), 500
    finally:
        if con:
            con.close()

@app.route('/carrinho/atualizar_quantidade', methods=['PUT'])
def atualizar_quantidade_carrinho():
    """
    Atualiza a quantidade de um item específico no carrinho de um usuário.
    Se a quantidade for 0 ou menos, o item é removido.
    Recebe usuario_id, item_id e nova_quantidade via JSON.
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    item_id = data.get('item_id')
    nova_quantidade = data.get('quantidade') # Renomeado para 'quantidade' para consistência

    if not all([usuario_id, item_id, nova_quantidade is not None]):
        return jsonify({'message': 'Dados incompletos para atualizar quantidade no carrinho.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()

        if nova_quantidade <= 0:
            # Remove o item se a quantidade for zero ou negativa
            delete_query = 'DELETE FROM Carrinho WHERE usuario_id = %s AND item_id = %s'
            cursor.execute(delete_query, (usuario_id, item_id))
            con.commit()
            if cursor.rowcount > 0:
                return jsonify({'message': 'Item removido do carrinho (quantidade zero).'}), 200
            else:
                return jsonify({'message': 'Item não encontrado no carrinho para remoção.'}), 404
        else:
            # Atualiza a quantidade do item
            update_query = 'UPDATE Carrinho SET quantidade = %s WHERE usuario_id = %s AND item_id = %s'
            cursor.execute(update_query, (nova_quantidade, usuario_id, item_id))
            con.commit()
            if cursor.rowcount > 0:
                return jsonify({'message': 'Quantidade do item no carrinho atualizada com sucesso!'}), 200
            else:
                return jsonify({'message': 'Item não encontrado no carrinho para atualização.'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar quantidade no carrinho: {err}")
        return jsonify({'message': 'Erro interno ao atualizar quantidade no carrinho.'}), 500
    finally:
        if con:
            con.close()

@app.route('/carrinho/remover_item', methods=['DELETE'])
def remover_item_carrinho():
    """
    Remove um item específico do carrinho de um usuário.
    Recebe usuario_id e item_id via JSON.
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    item_id = data.get('item_id')

    if not all([usuario_id, item_id]):
        return jsonify({'message': 'Dados incompletos para remover item do carrinho.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()
        delete_query = 'DELETE FROM Carrinho WHERE usuario_id = %s AND item_id = %s'
        cursor.execute(delete_query, (usuario_id, item_id))
        con.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Item removido do carrinho com sucesso!'}), 200
        else:
            return jsonify({'message': 'Item não encontrado no carrinho.'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao remover item do carrinho: {err}")
        return jsonify({'message': 'Erro interno ao remover item do carrinho.'}), 500
    finally:
        if con:
            con.close()

@app.route('/carrinho/<int:usuario_id>', methods=['GET'])
def listar_carrinho(usuario_id):
    """
    Lista todos os itens no carrinho de um usuário específico.
    Inclui informações detalhadas dos itens do cardápio e o subtotal.
    """
    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True) # Retorna linhas como dicionários

        query = '''
            SELECT
                C.id AS carrinho_item_id,  -- Renomeado para evitar conflito com I.id
                I.id AS item_id,
                I.nome,
                I.preco,
                C.quantidade,
                (C.quantidade * I.preco) as subtotal
            FROM Carrinho C
            JOIN ItemCardapio I ON C.item_id = I.id
            WHERE C.usuario_id = %s
        '''
        cursor.execute(query, (usuario_id,))
        itens = cursor.fetchall()

        # Hardcoding de caminhos de imagem para os itens do carrinho também
        image_paths = {
            1: '/views/static/imgs/shop1.png', # Sorvete de Baunilha
            2: '/views/static/imgs/shop2.png', # Salada de Frango
            3: '/views/static/imgs/shop3.png', # Rolinho Primavera
            4: '/views/static/imgs/shop4.png', # Cogumelos Recheados
            5: '/views/static/imgs/shop5.png', # Pão de Alho
            6: '/views/static/imgs/shop6.png', # Refogado de Legumes
        }

        # Adiciona o caminho da imagem a cada item do carrinho
        for item in itens:
            item['image'] = image_paths.get(item['item_id'], '/views/static/imgs/placeholder.png')

        return jsonify(itens), 200
    except mysql.connector.Error as err:
        print(f"Erro ao listar carrinho: {err}")
        return jsonify({'message': 'Erro interno ao listar carrinho.'}), 500
    finally:
        if con:
            con.close()

@app.route('/carrinho/limpar/<int:usuario_id>', methods=['DELETE'])
def limpar_carrinho(usuario_id):
    """
    Limpa todos os itens do carrinho de um usuário específico.
    """
    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()
        delete_query = 'DELETE FROM Carrinho WHERE usuario_id = %s'
        cursor.execute(delete_query, (usuario_id,))
        con.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Carrinho limpo com sucesso!'}), 200
        else:
            return jsonify({'message': 'Carrinho já vazio ou usuário não encontrado.'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao limpar carrinho: {err}")
        return jsonify({'message': 'Erro interno ao limpar carrinho.'}), 500
    finally:
        if con:
            con.close()


# ----------------- PEDIDO ----------------- #
@app.route('/pedido/criar', methods=['POST'])
def criar_pedido():
    """
    Cria um novo pedido com base nos itens do carrinho do usuário.
    Recebe usuario_id via JSON. O status inicial é 'PENDENTE' (Não Pago).
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')

    if not usuario_id:
        return jsonify({'message': 'ID do usuário é obrigatório para criar pedido.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)

        # 1. Listar itens do carrinho do usuário
        cart_query = '''
            SELECT
                C.item_id,
                C.quantidade,
                I.preco
            FROM Carrinho C
            JOIN ItemCardapio I ON C.item_id = I.id
            WHERE C.usuario_id = %s
        '''
        cursor.execute(cart_query, (usuario_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({'message': 'Carrinho do usuário está vazio. Adicione itens antes de criar um pedido.'}), 400

        valor_total_pedido = sum(item['preco'] * item['quantidade'] for item in cart_items)
        status_pedido = 'PENDENTE' # Conforme sua observação

        # 2. Inserir o pedido principal na tabela Pedido
        # Nota: Sua tabela Pedido atual parece ser para um item por pedido.
        # Para múltiplos itens, precisaríamos de uma tabela PedidoItem separada.
        # Por enquanto, vou inserir um pedido para CADA item no carrinho,
        # somando o valor total do pedido a cada item. Isso não é o ideal para um sistema de pedidos.
        # O ideal seria um Pedido (ID, usuario_id, valor_total, status)
        # e uma PedidoItem (ID, pedido_id, item_id, quantidade, subtotal_item).
        # Para manter a compatibilidade com sua estrutura atual, farei uma inserção por item.
        
        # Inserir cada item do carrinho como um registro separado na tabela Pedido
        for item in cart_items:
            insert_pedido_query = '''
                INSERT INTO Pedido (status, valorTotal, usuario_id, item_id, quantidade)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_pedido_query, (status_pedido, valor_total_pedido, usuario_id, item['item_id'], item['quantidade']))

        con.commit()

        # 3. Limpar o carrinho após a criação do pedido
        clear_cart_query = 'DELETE FROM Carrinho WHERE usuario_id = %s'
        cursor.execute(clear_cart_query, (usuario_id,))
        con.commit()

        return jsonify({'message': f'Pedido criado com sucesso para o usuário {usuario_id}! Total: R$ {valor_total_pedido:.2f}'}), 201
    except mysql.connector.Error as err:
        con.rollback() # Reverte em caso de erro
        print(f"Erro ao criar pedido: {err}")
        return jsonify({'message': 'Erro interno ao criar pedido.'}), 500
    finally:
        if con:
            con.close()

@app.route('/pedido/<int:usuario_id>', methods=['GET'])
def listar_pedidos(usuario_id):
    """
    Lista os pedidos de um usuário específico.
    """
    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        query = '''
            SELECT P.id, I.nome, P.quantidade, P.valorTotal, P.status, P.criadoEm
            FROM Pedido P
            JOIN ItemCardapio I ON P.item_id = I.id
            WHERE P.usuario_id = %s
            ORDER BY P.criadoEm DESC
        '''
        cursor.execute(query, (usuario_id,))
        pedidos = cursor.fetchall()
        return jsonify(pedidos), 200
    except mysql.connector.Error as err:
        print(f"Erro ao listar pedidos: {err}")
        return jsonify({'message': 'Erro interno ao listar pedidos.'}), 500
    finally:
        if con:
            con.close()

# ----------------- PAGAMENTO ----------------- #
@app.route('/pagamento/registrar', methods=['POST'])
def registrar_pagamento():
    """
    Registra um pagamento para um pedido específico.
    Atualiza o status do pedido para 'PAGO'.
    Recebe metodo, valor, status e pedido_id via JSON.
    """
    data = request.get_json()
    metodo = data.get('metodo')
    valor = data.get('valor')
    status = data.get('status')
    pedido_id = data.get('pedido_id')

    if not all([metodo, valor, status, pedido_id]):
        return jsonify({'message': 'Dados incompletos para registrar pagamento.'}), 400

    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor()

        # 1. Registrar o pagamento
        insert_pagamento_query = 'INSERT INTO Pagamento (metodo, valor, status, pedido_id) VALUES (%s, %s, %s, %s)'
        cursor.execute(insert_pagamento_query, (metodo, valor, status, pedido_id))

        # 2. Atualizar o status do pedido para 'PAGO'
        update_pedido_status_query = "UPDATE Pedido SET status = 'PAGO' WHERE id = %s"
        cursor.execute(update_pedido_status_query, (pedido_id,))

        con.commit()
        return jsonify({'message': 'Pagamento registrado e status do pedido atualizado com sucesso!'}), 201
    except mysql.connector.Error as err:
        con.rollback()
        print(f"Erro ao registrar pagamento: {err}")
        return jsonify({'message': 'Erro interno ao registrar pagamento.'}), 500
    finally:
        if con:
            con.close()

@app.route('/pagamento/<int:pedido_id>', methods=['GET'])
def obter_pagamento(pedido_id):
    """
    Obtém os detalhes de pagamento para um pedido específico.
    """
    con = None
    try:
        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT metodo, valor, status, criadoEm FROM Pagamento WHERE pedido_id = %s', (pedido_id,))
        pagamento = cursor.fetchone()

        if pagamento:
            return jsonify(pagamento), 200
        else:
            return jsonify({'message': 'Pagamento não encontrado para o pedido.'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao obter pagamento: {err}")
        return jsonify({'message': 'Erro interno ao obter pagamento.'}), 500
    finally:
        if con:
            con.close()


if __name__ == '__main__':
    app.run(debug=True)
