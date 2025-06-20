// views/static/js/cartService.js
// Este serviço é responsável por gerenciar o status de login e operações de carrinho com a API Flask.
angular.module('takeOutApp').factory('cartService', function($http, $q, $rootScope, $window) {
    // A chave para armazenar o usuário atual (obtido após o login) no localStorage
    const CURRENT_USER_STORAGE_KEY = 'currentUser';

    /**
     * Obtém o ID do usuário logado do localStorage.
     * Retorna null se nenhum usuário estiver logado.
     * @returns {string|number|null} O ID do usuário logado.
     */
    function getUserId() {
        try {
            const currentUser = $window.localStorage.getItem(CURRENT_USER_STORAGE_KEY);
            if (currentUser) {
                const userData = JSON.parse(currentUser);
                // Verifica se o userData tem a propriedade 'id' e se não é null/undefined
                if (userData && userData.id) {
                    console.log("cartService: getUserId() - ID encontrado no localStorage:", userData.id);
                    return userData.id;
                }
            }
            console.log("cartService: getUserId() - Usuário não logado (localStorage vazio ou ID ausente). Retornando null.");
            return null; // Retorna null se não houver currentUser ou ID
        } catch (e) {
            console.error("cartService: Erro ao obter ID do usuário do localStorage:", e);
            return null;
        }
    }

    /**
     * Emite um evento para notificar que o carrinho foi atualizado.
     */
    function broadcastCartUpdate() {
        $rootScope.$broadcast('cart:updated');
    }

    /**
     * Adiciona um item ao carrinho ou atualiza sua quantidade através da API.
     */
    function addItem(item, quantity = 1) {
        const userId = getUserId();
        if (!userId) {
            return $q.reject('Usuário não logado. Por favor, faça login para adicionar itens ao carrinho.');
        }

        const payload = {
            usuario_id: userId,
            item_id: item.id,
            quantidade: quantity
        };

        return $http.post('/carrinho/adicionar', payload)
            .then(function(response) {
                broadcastCartUpdate();
                return response.data;
            })
            .catch(function(error) {
                console.error("cartService: Erro ao adicionar item ao carrinho na API:", error);
                return $q.reject(error.data ? error.data.message : 'Erro ao adicionar item ao carrinho.');
            });
    }

    /**
     * Remove um item do carrinho através da API.
     */
    function removeItem(itemId) {
        const userId = getUserId();
        if (!userId) {
            return $q.reject('Usuário não logado.');
        }

        const payload = {
            usuario_id: userId,
            item_id: itemId
        };

        return $http.delete('/carrinho/remover_item', { data: payload, headers: { 'Content-Type': 'application/json' } })
            .then(function(response) {
                broadcastCartUpdate();
                return response.data;
            })
            .catch(function(error) {
                console.error("cartService: Erro ao remover item do carrinho na API:", error);
                return $q.reject(error.data ? error.data.message : 'Erro ao remover item do carrinho.');
            });
    }

    /**
     * Atualiza a quantidade de um item específico no carrinho através da API.
     */
    function updateQuantity(itemId, newQuantity) {
        const userId = getUserId();
        if (!userId) {
            return $q.reject('Usuário não logado.');
        }

        const payload = {
            usuario_id: userId,
            item_id: itemId,
            quantidade: newQuantity
        };

        return $http.put('/carrinho/atualizar_quantidade', payload)
            .then(function(response) {
                broadcastCartUpdate();
                return response.data;
            })
            .catch(function(error) {
                console.error("cartService: Erro ao atualizar quantidade no carrinho na API:", error);
                return $q.reject(error.data ? error.data.message : 'Erro ao atualizar quantidade no carrinho.');
            });
    }

    /**
     * Retorna todos os itens atualmente no carrinho de um usuário através da API.
     */
    function getCartItems() {
        const userId = getUserId();
        if (!userId) {
            console.log("cartService: getCartItems - Não há userId. Retornando array vazio.");
            return $q.resolve([]); // Retorna uma promessa resolvida com um array vazio se não houver usuário logado
        }
        console.log(`cartService: getCartItems - Buscando itens do carrinho para userId: ${userId}`);
        return $http.get(`/carrinho/${userId}`)
            .then(function(response) {
                return response.data;
            })
            .catch(function(error) {
                console.error("cartService: Erro ao carregar itens do carrinho da API:", error);
                return $q.reject(error.data ? error.data.message : 'Erro ao carregar itens do carrinho.');
            });
    }

    /**
     * Calcula e retorna o preço total de todos os itens no carrinho, buscando da API.
     */
    function getCartTotal() {
        return getCartItems().then(function(items) {
            return items.reduce((total, item) => total + (item.preco * item.quantity), 0);
        }).catch(function(error) {
            return $q.reject(error);
        });
    }

    /**
     * Limpa completamente o carrinho de um usuário através da API.
     */
    function clearCart() {
        const userId = getUserId();
        if (!userId) {
            return $q.reject('Usuário não logado.');
        }

        return $http.delete(`/carrinho/limpar/${userId}`)
            .then(function(response) {
                broadcastCartUpdate();
                return response.data;
            })
            .catch(function(error) {
                console.error("cartService: Erro ao limpar carrinho na API:", error);
                return $q.reject(error.data ? error.data.message : 'Erro ao limpar carrinho.');
            });
    }

    // Retorna a interface pública do serviço
    return {
        addItem: addItem,
        removeItem: removeItem,
        updateQuantity: updateQuantity,
        getCartItems: getCartItems,
        getCartTotal: getCartTotal,
        clearCart: clearCart,
        getUserId: getUserId // Expor o método para verificar se o usuário está logado
    };
});
