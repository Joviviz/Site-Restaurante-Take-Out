const app = angular.module("takeOutApp", ['ngRoute']); // Define o módulo e suas dependências

angular.module('takeOutApp').config(['$routeProvider', // Configura as rotas
    function config($routeProvider){
        $routeProvider.
        when('/home', {
            templateUrl: '/views/home.html' // Caminho da view para a rota home
            // Adicione um controlador aqui se tiver um para a home
            // controller: 'HomeController'
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
            templateUrl: '/views/menu.html' // Caminho da view para a rota do menu
            // Adicione um controlador aqui se tiver um para o menu
            // controller: 'MenuController'
        }).
        when('/cart', {
            templateUrl: '/views/cart.html' // Caminho da view para a rota do carrinho
            // Adicione um controlador aqui se tiver um para o carrinho
            // controller: 'CartController'
        }).
        otherwise('/home'); // Redireciona para a home se a rota não for encontrada
    }
]);