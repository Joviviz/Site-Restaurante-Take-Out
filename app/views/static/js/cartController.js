// views/static/js/cartController.js
// Este controlador agora busca os itens do carrinho da API Flask
// através do cartService, e permite a manipulação desses itens, com base no status de login.
angular.module('takeOutApp').controller('CartController', function($scope, cartService, $window, $rootScope, $http) {
    $scope.cartItems = [];
    $scope.cartTotal = 0;
    $scope.message = '';
    $scope.userId = null; // Armazena o ID do usuário no escopo para uso no HTML (ng-if, ng-disabled)

    /**
     * Carrega os itens do carrinho e calcula o total usando o cartService.
     * Esta função é chamada na inicialização e após cada modificação no carrinho.
     */
    $scope.loadCart = function() {
        $scope.userId = cartService.getUserId(); // Atualiza o userId no escopo
        console.log("CartController: loadCart - Verificando userId:", $scope.userId);

        if (!$scope.userId) {
            // Se não estiver logado, não tenta carregar da API, apenas zera a UI
            $scope.message = 'Você precisa estar logado para ver e gerenciar seu carrinho.';
            $scope.cartItems = [];
            $scope.cartTotal = 0;
            return; // Interrompe a execução se não estiver logado
        }

        // Se o usuário estiver logado, tenta buscar os itens da API
        cartService.getCartItems()
            .then(function(items) {
                // Mapeia os itens para garantir que 'preco' e 'quantity' sejam números
                // e que o nome da propriedade 'quantidade' do backend seja 'quantity' no frontend.
                $scope.cartItems = items.map(item => ({
                    ...item, // Copia todas as propriedades existentes
                    preco: parseFloat(item.preco), // Converte 'preco' para número de ponto flutuante
                    quantity: parseInt(item.quantidade) // CORRIGIDO: Converte 'quantidade' (do backend) para 'quantity' (do frontend)
                }));

                $scope.cartTotal = $scope.cartItems.reduce((total, item) => total + (item.preco * item.quantity), 0);
                $scope.message = ''; // Limpa mensagens se o carrinho for carregado com sucesso
                console.log("CartController: Carrinho carregado da API (após conversão e mapeamento):", $scope.cartItems);
            })
            .catch(function(errorMsg) {
                console.error("CartController: Erro ao carregar carrinho:", errorMsg);
                $scope.message = errorMsg; // Exibe o erro na UI
                $scope.cartItems = []; // Limpa o carrinho na UI em caso de erro
                $scope.cartTotal = 0;
            });
    };

    /**
     * Incrementa a quantidade de um item no carrinho.
     */
    $scope.incrementQuantity = function(item) {
        // As validações de login já estão no cartService, mas reforçar aqui é bom para feedback imediato
        if (!$scope.userId) { $scope.message = 'Você precisa estar logado para alterar a quantidade.'; return; }
        // Note que item.item_id é o ID do produto, não o ID da linha do carrinho
        cartService.updateQuantity(item.item_id, item.quantity + 1)
            .then(function() { $scope.loadCart(); })
            .catch(function(errorMsg) {
                console.error("CartController: Erro ao incrementar quantidade:", errorMsg);
                alert(`ERRO: ${errorMsg}`);
                $scope.message = errorMsg;
            });
    };

    /**
     * Decrementa a quantidade de um item no carrinho.
     */
    $scope.decrementQuantity = function(item) {
        if (!$scope.userId) { $scope.message = 'Você precisa estar logado para alterar a quantidade.'; return; }
        // Note que item.item_id é o ID do produto, não o ID da linha do carrinho
        cartService.updateQuantity(item.item_id, item.quantity - 1)
            .then(function() { $scope.loadCart(); })
            .catch(function(errorMsg) {
                console.error("CartController: Erro ao decrementar quantidade:", errorMsg);
                alert(`ERRO: ${errorMsg}`);
                $scope.message = errorMsg;
            });
    };

    /**
     * Remove um item do carrinho.
     */
    $scope.removeItem = function(item) {
        if (!$scope.userId) { $scope.message = 'Você precisa estar logado para remover itens.'; return; }
        if ($window.confirm(`Tem certeza que deseja remover ${item.name} do carrinho?`)) {
            // Note que item.item_id é o ID do produto, não o ID da linha do carrinho
            cartService.removeItem(item.item_id)
                .then(function() { $scope.loadCart(); })
                .catch(function(errorMsg) {
                    console.error("CartController: Erro ao remover item:", errorMsg);
                    alert(`ERRO: ${errorMsg}`);
                    $scope.message = errorMsg;
                });
        }
    };

    /**
     * Redireciona para a tela de checkout e cria um pedido.
     */
    $scope.goToCheckout = function() {
        if (!$scope.userId) { $scope.message = 'Você precisa estar logado para finalizar o pedido.'; return; }
        if ($scope.cartItems.length === 0) {
            $scope.message = 'Seu carrinho está vazio. Adicione itens antes de finalizar o pedido.';
            alert('AVISO: Seu carrinho está vazio. Adicione itens antes de finalizar o pedido.');
            return;
        }

        $http.post('/pedido/criar', { usuario_id: $scope.userId })
            .then(function(response) {
                $scope.message = response.data.message;
                alert(response.data.message + ' Prossiga para o pagamento na próxima etapa.');
                $scope.loadCart();
            })
            .catch(function(error) {
                console.error("CartController: Erro ao criar pedido:", error);
                const errorMessage = error.data ? error.data.message : 'Erro ao finalizar o pedido. Verifique o console.';
                $scope.message = errorMessage;
                alert(`ERRO ao criar pedido: ${errorMessage}`);
                if (error.data && error.data.message.includes('Carrinho do usuário está vazio')) {
                    $scope.loadCart();
                }
            });
    };

    $scope.loadCart(); // Carrega o carrinho na inicialização

    // Ouve por atualizações do carrinho de outros controllers (ex: MenuController)
    $rootScope.$on('cart:updated', function() {
        console.log("CartController: Evento 'cart:updated' recebido. Recarregando carrinho...");
        $scope.loadCart();
    });
});
