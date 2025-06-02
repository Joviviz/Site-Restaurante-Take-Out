from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Brilha Ericao esse aqui eh o arquivo
app = Flask(__name__)
CORS(app, supports_credentials=True)

db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',  
    'database': 'takeout_db'
}

# Chave secreta para sessões
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = True

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Rota principal que serve o index.html
@app.route('/')
def index():
    return render_template('index.html')

# API para login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['role'] = account['role']
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': account['id'],
                    'email': account['email'],
                    'role': account['role'],
                    'name': account['name']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
    except Error as e:
        print(f"Erro no login: {e}")
        return jsonify({'success': False, 'message': 'Erro no servidor'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API para logout
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

# API para verificar sessão
@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'loggedin' in session:
        connection = get_db_connection()
        if not connection:
            return jsonify({'loggedin': False})
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT id, name, email, role FROM users WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            
            if account:
                return jsonify({
                    'loggedin': True,
                    'user': {
                        'id': account['id'],
                        'name': account['name'],
                        'email': account['email'],
                        'role': account['role']
                    }
                })
        except Error as e:
            print(f"Erro ao verificar sessão: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({'loggedin': False})

# API para registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'As senhas não coincidem'}), 400
    
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({'success': False, 'message': 'Email inválido'}), 400
    
    hashed_password = generate_password_hash(password)
    role = 'user'  # Por padrão, novos usuários são 'user'
    created_at = datetime.now()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verifica se o email já existe
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
        
        # Insere o novo usuário
        cursor.execute('''
            INSERT INTO users (name, email, password, role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (name, email, hashed_password, role, created_at))
        
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registro realizado com sucesso'
        })
    except Error as e:
        print(f"Erro no registro: {e}")
        connection.rollback()
        return jsonify({'success': False, 'message': 'Erro no servidor'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)