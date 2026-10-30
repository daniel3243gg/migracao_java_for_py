# Clientes

## Cadastro

**Condição.** O payload deve conter `nome` e `cpf` não nulos e não vazios após `trim`.

**Comportamento e dados alterados.** O registro é inserido em `clientes`; `telefone` e `email` são opcionais. O banco gera o `id`. Em sucesso, o controller retorna o cliente criado (`201`).

**Bloqueios e resultados.** CPF repetido viola `UNIQUE` e é convertido pelo controller em `409` com `CPF já cadastrado`. O schema também exige `nome` e `cpf` (`NOT NULL`), mas não há validação de formato, tamanho efetivo, normalização ou validação de telefone/email.

**Fonte.** `ClienteController.handleCreate`, `ClienteRepository.save`, `clientes.cpf` em `database/init.sql`.

## Consulta e alteração

Consultas por lista são ordenadas por nome; a consulta por ID retorna `404` quando o registro não existe. A alteração exige novamente `nome` e `cpf` não vazios, substitui nome, CPF, telefone e email e retorna `404` se o ID não existir. A unicidade do CPF continua sendo aplicada pelo banco, mas a alteração não traduz explicitamente uma violação de CPF em `409`; ela cai no tratamento genérico de erro SQL.

## Exclusão e efeito sobre veículos

Sem dependências, a exclusão remove o cliente e retorna mensagem de sucesso; ID inexistente retorna `404`.

O relacionamento `veiculos.cliente_id` é `REFERENCES clientes(id) ON DELETE CASCADE`. Portanto, ao excluir um cliente, os veículos vinculados são apagados automaticamente, sujeito às dependências que esses veículos tenham em `permanencias`.

**Inconsistência/limitação.** O controller captura violação de chave estrangeira e informa `Não é possível excluir cliente com veículos cadastrados`, mas o schema autoriza a cascata dos veículos. Assim, um cliente com veículos sem permanências tende a ser excluído com seus veículos; se os veículos possuírem permanências, a cascata é impedida pela FK de permanências e o resultado tende a ser `409`. A mensagem não descreve fielmente todos os casos.

## Fonte

`ClienteController`, `ClienteRepository`, modelo `Cliente` e tabelas `clientes`/`veiculos` em `database/init.sql`.
