// app/views/static/js/loginController.js
angular.module('takeOutApp').controller('LoginController', function($scope, $http, $window) {
    // Inicializa o objeto user para armazenar os dados do formulário de login
    $scope.user = {
        email: '',
        senha: ''
    };
    $scope.message = ''; // Para exibir mensagens de erro/sucesso na UI

    // Função para lidar com o processo de login
    $scope.login = function() {
        console.log('Tentando logar com:', $scope.user.email); // Log para depuração

        // Faz uma requisição POST para a API de login
        $http.post('/usuarios/login', $scope.user)
            .then(function(response) {
                // Callback para sucesso da requisição HTTP (status 2xx)
                if (response.status === 200) {
                    console.log('Login bem-sucedido!', response.data);
                    // Armazena os dados do usuário (ID, nome, cargo) no localStorage
                    localStorage.setItem('currentUser', JSON.stringify(response.data.usuario));
                    $scope.message = 'Login bem-sucedido!';
                    // Redireciona o usuário para a página de menu após o login
                    $window.location.href = '#!menu';
                } else {
                    // Trata outros status de sucesso que não 200 (se aplicável, mas geralmente 200 é o esperado para login bem-sucedido)
                    $scope.message = response.data.message || 'Erro ao logar.';
                    console.error('Erro de login:', response.data);
                }
            })
            .catch(function(error) {
                // Callback para erro da requisição HTTP (ex: erro de rede, status 4xx, 5xx)
                // Exibe a mensagem de erro da API ou uma mensagem genérica
                $scope.message = error.data ? error.data.message : 'Erro de conexão com o servidor. Tente novamente.';
                console.error('Erro na requisição de login:', error);
            });
    };
});