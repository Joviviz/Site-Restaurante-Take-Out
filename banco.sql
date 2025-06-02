CREATE DATABASE takeout_db;
USE takeout_db;

-- Usuário
CREATE TABLE Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    criadoEm DATETIME DEFAULT CURRENT_TIMESTAMP,
    role ENUM('CLIENTE', 'FUNCIONARIO') NOT NULL
);

-- ItemCardápio
CREATE TABLE ItemCardapio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    disponivel BOOLEAN DEFAULT TRUE,
    criadoEm DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id)
);

-- Carrinho
CREATE TABLE Carrinho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    item_id INT NOT NULL,
    quantidade INT DEFAULT 1,
    criadoEm DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id),
    FOREIGN KEY (item_id) REFERENCES ItemCardapio(id)
);

-- Pedido
CREATE TABLE Pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    valorTotal DECIMAL(10,2) NOT NULL,
    criadoEm DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT NOT NULL,
    item_id INT NOT NULL,
    quantidade INT DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id),
    FOREIGN KEY (item_id) REFERENCES ItemCardapio(id)
);

-- Pagamento
CREATE TABLE Pagamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metodo VARCHAR(50) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    criadoEm DATETIME DEFAULT CURRENT_TIMESTAMP,
    pedido_id INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES Pedido(id)
);