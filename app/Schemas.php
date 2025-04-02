<?php

namespace App;
class Schemas {


    public function usersSchema() {
        $table = 'users';

        $schema = [
            'id' => ['intType'],
            'username' => ['stringType', 'length' => [1, 300]],
            'email' => ['stringType', 'length' => [1, 150]],
            'password' => ['stringType', 'noWhiteSpace', 'length' => [3, 255]],
            'role' => ['stringType'],
        ];
    
        $hidden = ['password'];

        return [
            'schema' => $schema,
            'hidden' => $hidden,
            'table' => $table,
        ];
    }

    public static function getSchema($table) {
        $instance = new self();
        $result = $instance->{$table.'Schema'}();
        return $result;
    }
}