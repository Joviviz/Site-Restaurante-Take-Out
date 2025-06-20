// views/static/js/menuController.js
// Este controlador lida com a exibição do cardápio e a adição de itens ao carrinho.
angular.module('takeOutApp').controller('MenuController', function($scope, $http, cartService, $window) {
    // Dados mockados para o cardápio, pois o SQL não pode ser alterado/populado.
    $scope.menuItems = [
        { id: 1, name: 'Sorvete de Baunilha', price: 25.00, image: '/views/static/imgs/shop1.png', quantityInMenu: 0 },
        { id: 2, name: 'Salada de Frango', price: 80.00, image: '/views/static/imgs/shop2.png', quantityInMenu: 0 },
        { id: 3, name: 'Rolinho Primavera', price: 50.00, image: '/views/static/imgs/shop3.png', quantityInMenu: 0 },
        { id: 4, name: 'Cogumelos Recheados', price: 40.00, image: '/views/static/imgs/shop4.png', quantityInMenu: 0 },
        { id: 5, name: 'Pão de Alho', price: 30.00, image: '/views/static/imgs/shop5.png', quantityInMenu: 0 },
        { id: 6, name: 'Refogado de Legumes', price: 60.00, image: '/views/static/imgs/shop6.png', quantityInMenu: 0 }
    ];

    $scope.message = ''; // Para exibir mensagens de sucesso ou erro ao usuário

    /**
     * Carrega os itens do menu (atualmente mockados).
     */
    $scope.loadMenuItems = function() {
        console.log("MenuController: Itens do menu carregados (dados mockados).");
        // Se no futuro precisar buscar da API, use:
        /*
        $http.get('/cardapio')
            .then(function(response) {
                $scope.menuItems = response.data.map(item => ({
                    id: item.id, name: item.nome, price: item.preco, image: item.image, quantityInMenu: 0
                }));
            })
            .catch(function(error) {
                console.error('MenuController: Erro ao carregar itens do menu da API:', error);
                $scope.message = 'Erro ao carregar cardápio. Tente novamente mais tarde.';
            });
        */
    };

    /**
     * Atualiza a quantidade de um item diretamente na exibição do cardápio.
     */
    $scope.updateQuantityInMenu = function(item, delta) {
        item.quantityInMenu = Math.max(0, item.quantityInMenu + delta);
        $scope.message = '';
        console.log(`MenuController: Quantidade de ${item.name} atualizada para: ${item.quantityInMenu}`);
    };

    /**
     * Adiciona um item ao carrinho usando o cartService.
     */
    $scope.addToCart = function(item) {
        console.log("MenuController: addToCart chamado para:", item.name, "Quantidade:", item.quantityInMenu);

        if (item.quantityInMenu > 0) {
            const cartItem = {
                id: item.id,
                name: item.name,
                preco: item.price,
                image: item.image
            };

            console.log("MenuController: Tentando adicionar ao carrinho via cartService.addItem com payload:", cartItem, "Quantidade:", item.quantityInMenu);

            cartService.addItem(cartItem, item.quantityInMenu)
                .then(function(response) {
                    console.log("MenuController: Promessa de addItem resolvida com sucesso:", response);
                    $scope.message = `${cartItem.name} (${item.quantityInMenu}x) adicionado ao carrinho!`;
                    alert(`SUCESSO: ${cartItem.name} (${item.quantityInMenu}x) adicionado ao carrinho!`);
                    item.quantityInMenu = 0;
                })
                .catch(function(errorMsg) {
                    console.error("MenuController: Promessa de addItem rejeitada com erro:", errorMsg);
                    $scope.message = errorMsg;
                    alert(`ERRO: ${errorMsg}`);
                    // Se o erro for "Usuário não logado", redireciona para a página de login
                    if (typeof errorMsg === 'string' && errorMsg.includes('Usuário não logado')) {
                        console.log("MenuController: Redirecionando para a página de login.");
                        $window.location.href = '#!login';
                    }
                });
        } else {
            $scope.message = 'Por favor, selecione uma quantidade para adicionar ao carrinho.';
            alert('AVISO: Por favor, selecione uma quantidade para adicionar ao carrinho.');
            console.log("MenuController: Quantidade para adicionar ao carrinho é 0 ou menos.");
        }
    };

    $scope.loadMenuItems();
});
