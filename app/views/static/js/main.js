const app = angular.module("takeOutApp", ['ngRoute']);

angular.module('takeOutApp').config(['$routeProvider', 
        function config($routeProvider){
            $routeProvider.
            when('/home', {
                templateUrl: '/views/home.html'
            }).
            when('/login', {
                templateUrl: '/views/login.html'            
            }).
            when('/register', {
                templateUrl: '/views/register.html'
            }).
            when('/menu', {
                templateUrl: '/views/menu.html'
            }).
            when('/cart', {
                templateUrl: '/views/cart.html'
            }).
            when('/about', {
                templateUrl: '/views/about.html'
            }).
            otherwise('/home')
        }
    ]);
