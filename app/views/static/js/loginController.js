// app/views/static/js/loginController.js
// Adiciona o controlador ao módulo 'takeOutApp' existente
angular.module('takeOutApp').controller('LoginController', function($scope, $http, $window) {
    $scope.user = {
        email: '',
        senha: ''
    };
    $scope.message = '';

    $scope.login = function() {
        console.log('Tentando logar com:', $scope.user.email);
        $http.post('/usuarios/login', $scope.user)
            .then(function(response) {
                if (response.status === 200) {
                    console.log('Login bem-sucedido!', response.data);
                    localStorage.setItem('currentUser', JSON.stringify(response.data.usuario));
                    $scope.message = 'Login bem-sucedido!';
                    $window.location.href = '#!menu'; // Redireciona para a página de menu
                } else {
                    $scope.message = response.data.message || 'Erro ao logar.';
                    console.error('Erro de login:', response.data);
                }
            })
            .catch(function(error) {
                $scope.message = error.data ? error.data.message : 'Erro de conexão com o servidor.';
                console.error('Erro na requisição de login:', error);
            });
    };
});