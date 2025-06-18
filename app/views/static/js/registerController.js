// app/views/static/js/registerController.js
// Adiciona o controlador ao módulo 'takeOutApp' existente
angular.module('takeOutApp').controller('RegisterController', function($scope, $http, $window) {
    $scope.newUser = {
        nome: '',
        email: '',
        senha: '',
        confirmarSenha: '',
        cargo: 'cliente'
    };
    $scope.message = '';
    $scope.isSuccess = false;

    $scope.register = function() {
        if ($scope.newUser.senha !== $scope.newUser.confirmarSenha) {
            $scope.message = 'As senhas não coincidem.';
            $scope.isSuccess = false;
            return;
        }

        const userData = {
            nome: $scope.newUser.nome,
            email: $scope.newUser.email,
            senha: $scope.newUser.senha,
            cargo: $scope.newUser.cargo
        };

        console.log('Tentando registrar com:', userData.email);
        $http.post('/usuarios/criar', userData)
            .then(function(response) {
                if (response.status === 201) {
                    console.log('Usuário registrado com sucesso!', response.data);
                    $scope.message = 'Registro bem-sucedido! Redirecionando para o login...';
                    $scope.isSuccess = true;
                    setTimeout(function() {
                        $window.location.href = '#!login';
                    }, 2000);
                } else {
                    $scope.message = response.data.message || 'Erro ao registrar.';
                    $scope.isSuccess = false;
                    console.error('Erro de registro:', response.data);
                }
            })
            .catch(function(error) {
                $scope.message = error.data ? error.data.message : 'Erro de conexão com o servidor.';
                $scope.isSuccess = false;
                console.error('Erro na requisição de registro:', error);
            });
    };
});