const app = angular.module("takeOutApp", ['ngRoute']);

angular.module('takeOutApp').config(['$routeProvider',
    function config($routeProvider) {
        $routeProvider.
        when('/main',{
            templateURL: 'public/views/main.html'
        }).
        otherwise('/home')
    }
]);