const app = angular.module("takeOutApp", ['ngRoute']);

angular.module('takeOutApp').config(['$routeProvider', 
        function config($routeProvider){
            $routeProvider.
            when('/home', {
                templateUrl: '/app/views/home.html'
            }).
            when('/login', {
                templateUrl: '/app/views/login.html'
            }).
            when('/register', {
                templateUrl: '/app/views/register.html'
            }).
            otherwise('/home')
        }
    ]);