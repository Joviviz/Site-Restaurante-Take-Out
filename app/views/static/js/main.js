const app = angular.module("takeOutApp", ['ngRoute']); // Define o módulo e suas dependências

angular.module('takeOutApp').config(['$routeProvider', // Configura as rotas
    function config($routeProvider){
        $routeProvider.
        when('/home', {
            templateUrl: '/views/home.html' // Caminho da view para a rota home
        }).
        when('/login', {
            templateUrl: '/views/login.html', // Caminho da view para a rota de login
            controller: 'LoginController'     // Associa o LoginController a esta rota
        }).
        when('/register', {
            templateUrl: '/views/register.html', // Caminho da view para a rota de registro
            controller: 'RegisterController'  // Associa o RegisterController a esta rota
        }).
        when('/menu', {
            templateUrl: '/views/menu.html', // Caminho da view para a rota do menu
            controller: 'MenuController'     // Associa o MenuController a esta rota
        }).
        when('/cart', {
            templateUrl: '/views/cart.html', // Caminho da view para a rota do carrinho
            controller: 'CartController'     // Associa o CartController a esta rota
        }).
        // NOVA ROTA: Adicionado o caminho para a página "Sobre Nós"
        when('/about', {
            templateUrl: '/views/about.html' // Caminho da view para a rota "Sobre Nós"
            // Se você tiver um controlador específico para a página "Sobre Nós",
            // pode adicioná-lo aqui (ex: controller: 'AboutController')
        }).
        otherwise('/home'); // Redireciona para a home se a rota não for encontrada
    }
]);
