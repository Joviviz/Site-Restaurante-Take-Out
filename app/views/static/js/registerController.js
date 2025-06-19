// app/views/static/js/registerController.js
angular.module('takeOutApp').controller('RegisterController', function($scope, $http, $window) {
    // Inicializa o objeto newUser para armazenar os dados do formulário de registro
    $scope.newUser = {
        nome: '',
        email: '',
        senha: '',
        confirmarSenha: '', // Campo para validação no frontend, não enviado para a API
        cargo: 'cliente'    // Define um cargo padrão para novos usuários
    };
    $scope.message = '';    // Para exibir mensagens de erro/sucesso
    $scope.isSuccess = false; // Flag para controlar a classe CSS da mensagem (sucesso ou erro)

    // Função para lidar com o processo de registro de um novo usuário
    $scope.register = function() {
        // Validação inicial: verifica se as senhas digitadas coincidem
        if ($scope.newUser.senha !== $scope.newUser.confirmarSenha) {
            $scope.message = 'As senhas não coincidem. Por favor, verifique.';
            $scope.isSuccess = false; // Define a mensagem como erro
            return; // Interrompe a execução se as senhas não coincidirem
        }

        // Prepara os dados do usuário para serem enviados à API (exclui confirmarSenha)
        const userData = {
            nome: $scope.newUser.nome,
            email: $scope.newUser.email,
            senha: $scope.newUser.senha,
            cargo: $scope.newUser.cargo
        };

        console.log('Tentando registrar com:', userData.email); // Log para depuração

        // Faz uma requisição POST para a API de criação de usuário
        $http.post('/usuarios/criar', userData)
            .then(function(response) {
                // Callback para sucesso da requisição HTTP (status 2xx)
                if (response.status === 201) { // 201 Created é o esperado para criação bem-sucedida
                    console.log('Usuário registrado com sucesso!', response.data);
                    $scope.message = 'Registro bem-sucedido! Redirecionando para o login...';
                    $scope.isSuccess = true; // Define a mensagem como sucesso
                    // Redireciona para a página de login após um pequeno atraso
                    setTimeout(function() {
                        $window.location.href = '#!login';
                    }, 2000); // Redireciona após 2 segundos
                } else {
                    // Trata outros status de sucesso que não 201 (se aplicável)
                    $scope.message = response.data.message || 'Erro ao registrar. Tente novamente.';
                    $scope.isSuccess = false; // Define a mensagem como erro
                    console.error('Erro de registro:', response.data);
                }
            })
            .catch(function(error) {
                // Callback para erro da requisição HTTP (ex: erro de rede, status 4xx, 5xx)
                $scope.message = error.data ? error.data.message : 'Erro de conexão com o servidor. Verifique sua conexão ou tente mais tarde.';
                $scope.isSuccess = false; // Define a mensagem como erro
                console.error('Erro na requisição de registro:', error);
            });
    };
});