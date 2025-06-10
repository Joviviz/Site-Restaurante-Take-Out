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
            when('/test', {
                templateUrl: '/views/test.html'
            }).
            otherwise('/home')
        }
    ]);
