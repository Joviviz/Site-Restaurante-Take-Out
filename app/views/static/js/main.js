const app = angular.module("takeOutApp", ['ngRoute']);

angular.module('takeOutApp').config(['$routeProvider',
    function config($routeProvider){
        $routeProvider.
        when('/home', {
            templateUrl: '/views/home.html'
            
        }).
        when('/login', {
            templateUrl: '/views/login.html',
            controller: 'LoginController' 
        }).
        when('/register', {
            templateUrl: '/views/register.html',
            controller: 'RegisterController' 
        }).
        when('/menu', {
            templateUrl: '/views/menu.html'

        }).
        when('/cart', {
            templateUrl: '/views/cart.html'

        }).
        otherwise('/home');
    }
]);