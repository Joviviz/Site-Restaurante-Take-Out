<?php

namespace App\Controllers;

use App\Schemas;
use Respect\Validation\Exceptions\ValidationException;
use Respect\Validation\Validator as v;
class CrudController
{

    public function getSchemaKeys($schema, $hidden = [])
    {
        $schemaKeys = array_keys($schema);
        foreach ($schemaKeys as $key) {
            if (in_array($key, $hidden)) {
                $index = array_search($key, haystack: $schemaKeys);
                if ($index !== FALSE) {
                    unset($schemaKeys[$index]);
                }
            }
        }
        return $schemaKeys;
    }

    public function schemaToValidator($schema, $method)
    {
        $validator = [];
        foreach ($schema as $key => $value) {
            $otp = null;
            if ($method == 'add' and $key == 'id') {
                continue;
            }
            if ($method == 'add' and $key == 'created_at') {
                continue;
            }

            // if(in_array())
            $optional = false;
            foreach ($value as $function) {
                if ($function == 'optional') {
                    $optional = true;

                }
            }
            foreach ($value as $index => $function) {


                $parameters = $function;
                if (is_numeric($index)) {
                    $function = $value[$index];
                    $parameters = [];
                } else {
                    $function = $index;
                }
                if ($optional == false) {
                    if ($otp == null) {
                        $otp = v::__callStatic($function, []);
                    } else {
                        $otp = $otp->__call($function, $parameters);
                    }
                }
            }
            if ($optional == false) {
                $validator[$key] = $otp;
            }
        }
        return validator($validator);
    }

    public function browse($table)
    {
        $data = [];
        $schema = Schemas::getSchema($table);
        $keys = $this->getSchemaKeys($schema['schema'], $schema['hidden']);
        $query = query();
        $query->select(implode(',', $keys));
        $query->from($schema['table']);
        try {
            $data = $query->fetchAllAssociative();
            echo json_encode([
                'status' => 200,
                'message' => $data
            ]);
        } catch (\Exception $e) {
            if ($e->getCode() == 1146) {
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => 'Table ' . $table . ' not found.'
                ]);
                return;
            }
        }
    }

    public function read($table, $id)
    {
        $data = [];
        $schema = Schemas::getSchema($table);
        $keys = $this->getSchemaKeys($schema['schema'], $schema['hidden']);
        $query = query();
        $query->select(implode(',', $keys));
        $query->from($schema['table']);
        $query->where('id = ?');
        $query->setParameter(0, $id);
        try {
            $data = $query->fetchAllAssociative();
            if (sizeof($data) > 0) {
                echo json_encode([
                    'status' => 200,
                    'message' => $data[0]
                ]);
                return true;
            } else {
                response()->setCode(403);
                echo json_encode([
                    'status' => 403,
                    'message' => ucfirst($table) . " of id " . $id . " not found."
                ]);
                return false;
            }
        } catch (\Exception $e) {
            if ($e->getCode() == 1146) {
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => 'Table ' . $table . ' not found.'
                ]);
                return false;
            } else {
                // dd($e);
                return false;
            }
        }
    }

    public function delete($table, $id)
    {
        $data = [];
        $schema = Schemas::getSchema($table);
        $keys = $this->getSchemaKeys($schema['schema'], $schema['hidden']);
        $query = query();
        $query->delete($schema['table']);
        $query->where('id = ?');
        $query->setParameter(0, $id);
        try {
            $data = $query->fetchAllAssociative();
            echo json_encode([
                'status' => 200,
                'message' => ucfirst($table) . " of id " . $id . " deleted successfully."
            ]);
            return;

        } catch (\Exception $e) {
            if ($e->getCode() == 1146) {
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => 'Table ' . $table . ' not found.'
                ]);
                return;
            } else {
                throw $e;
            }
        }
    }

    public function add($table)
    {
        $data = $_POST;

        $schema = Schemas::getSchema($table);

        $validator = $this->schemaToValidator($schema['schema'], 'add');
        try {
            $validator->check((object) $data);
            if(isset($data['questions'])) {
                $data['questions'] = json_encode($data['questions']);
            }
            if(isset($data['student_files'])) {
                $data['student_files'] = json_encode($data['student_files']);
            }
            // dd($data['questions']);
            if ($data['captcha']) {
                unset($data['captcha']);
            }
            if (isset($data['password'])) {
                $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT, ['cost' => 12]);
            }
            $keys = $this->getSchemaKeys($schema['schema'], $schema['hidden']);
            $post_keys = array_keys($data);
            $query = query();
            $mapped = array_combine($post_keys, array_fill(0, count($post_keys), '?'));
            $query->insert($schema['table'])->values($mapped);
            foreach ($post_keys as $index => $key) {
                if (isset($data[$key])) {
                    $query->setParameter($index, $data[$key]);
                }
            }
            $query->executeQuery();
        } catch (\Exception $e) {
            if ($e->getCode() == 1062) {
                $duplicated_column = explode("'", $e->getMessage())[3];
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => ucfirst($duplicated_column) . ' already exists.'
                ]);
                return;
            } else if ($e->getCode() == 1146) {
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => 'Table ' . $table . ' not found.'
                ]);
                return;
            } else if ($e->getCode() == 0) {
                response()->setCode(403);
                echo json_encode([
                    "status" => 403,
                    "error" => $e->getMessage()
                ]);
                return;
            } else {
                response()->setCode(403);
                echo json_encode([
                    "status" => 403,
                    "code" => $e->getCode(),
                    "error" => $e->getMessage()
                ]);
                return;
            }
        }
    }

    public function file() {
        if(isset($_FILES['file'])) {
            $file = $_FILES['file'];
            if($file['error'] == 0) {
                $temp_file_path = $file['tmp_name'];
                $file_ext_group = explode('.',$file['name']);
                $file_type = $file_ext_group[count($file_ext_group)-1];
                $file_new_path = '\\public\\uploads\\'.time().".".$file_type;
                $current_dir = $_SERVER['DOCUMENT_ROOT'].$file_new_path;
                echo json_encode([
                    "status" => 200,
                    "message" => implode('/',explode('\\',$file_new_path))
                ]);
                copy($temp_file_path,$current_dir);
                return;
                // dd($current_dir);
            }
        }
        echo json_encode([
            "status" => 403,
            "message" => "Not allowed."
        ]);
        return;
    }

    public function update($table, $id)
    {
        try {
            $data = request()->getPost();
        } catch(\Exception $e) {
            $data = $_POST;
        }

        $schema = Schemas::getSchema($table);

        // $validator = $this->schemaToValidator($schema['schema'], 'add');
        try {
            if(isset($data['student_files'])) {
                $data['student_files'] = json_encode($data['student_files']);
            }
            if ($data['captcha']) {
                unset($data['captcha']);
            }
            if (isset($data['password'])) {
                $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT, ['cost' => 12]);
            }
            $query = database();
            $query->update($schema['table'], $data, ['id' => $id]);
        } catch (\Exception $e) {
            if ($e->getCode() == 1062) {
                $duplicated_column = explode("'", $e->getMessage())[3];
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => ucfirst($duplicated_column) . ' already exists.'
                ]);
                return;
            } else if ($e->getCode() == 1146) {
                response()->setCode(400);
                echo json_encode([
                    'status' => 400,
                    'message' => 'Table ' . $table . ' not found.'
                ]);
                return;
            } else if ($e->getCode() == 0) {
                response()->setCode(403);
                echo json_encode([
                    "status" => 403,
                    "error" => $e->getMessage()
                ]);
                return;
            } else {
                response()->setCode(403);
                echo json_encode([
                    "status" => 403,
                    "code" => $e->getCode(),
                    "error" => $e->getMessage()
                ]);
                return;
            }
        }
    }
}