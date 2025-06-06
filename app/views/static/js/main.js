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
            otherwise('/home')
        }
    ]);


// Controller 

angular.module('takeOutApp').controller('AuthController', ['$scope', '$http', 
    function($scope, $http) {
        
        $scope.registro = {
            nome: '',
            email: '',
            senha: '',
            role: 'CLIENTE' 
        };
        
        $scope.login = {
            email: '',
            senha: ''
        };
        
        // Mensagens de feedback
        $scope.mensagem = '';
        $scope.erro = '';
        
        // Função para registrar usuário
        $scope.registrar = function() {
            $http.post('/usuarios/criar', $scope.registro)
                .then(function(response) {
                    $scope.mensagem = response.data.message;
                    $scope.erro = '';
                    // Redireciona para login após registro
                    window.location.hash = '#!/login';
                })
                .catch(function(error) {
                    $scope.erro = error.data.message || 'Erro ao registrar usuário';
                    $scope.mensagem = '';
                });
        };
        
        // Função para fazer login
        $scope.fazerLogin = function() {
            $http.post('/usuarios/login', $scope.login)
                .then(function(response) {
                    $scope.mensagem = response.data.message;
                    $scope.erro = '';
                    // Armazena os dados do usuário (simples, sem usar localStorage/sessionStorage)
                    $scope.usuarioLogado = response.data.usuario;
                    // Redireciona para home após login
                    window.location.hash = '#!/home';
                })
                .catch(function(error) {
                    $scope.erro = error.data.message || 'Credenciais inválidas';
                    $scope.mensagem = '';
                });
        };
    }
]);