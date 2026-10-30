# Veículos

## Cadastro e campos obrigatórios

**Condição.** `placa`, `marca`, `modelo`, `cor` devem ser não nulos e não vazios após `trim`; `clienteId` deve ser informado. Não há validação de formato de placa nem de existência do cliente antes do `INSERT`.

**Comportamento.** O veículo é inserido com vínculo ao cliente e recebe ID gerado pelo banco. A placa é única; repetição retorna `409` com `Placa já cadastrada`. O vínculo a cliente inexistente viola a FK e, como não é traduzido pelo controller, normalmente resulta em erro SQL `500`.

O schema limita os comprimentos a placa 10, marca/modelo 50 e cor 30, mas o controller não valida esses limites. O banco também exige todos esses campos e `cliente_id` (`NOT NULL`).

## Consulta e alteração

Listagens e consultas fazem `JOIN` com `clientes`, expondo também o nome do cliente, e a lista é ordenada por placa. ID inexistente retorna `404`.

A alteração exige os mesmos campos obrigatórios e pode trocar o cliente, a placa ou os dados descritivos. O ID inexistente retorna `404`; violações de unicidade ou de FK não recebem tratamento específico no caminho de atualização e caem no erro SQL genérico.

## Exclusão

ID inexistente retorna `404`. A exclusão de veículo com qualquer permanência registrada é bloqueada pela FK `permanencias.veiculo_id REFERENCES veiculos(id)` sem `ON DELETE CASCADE`; o controller converte a violação em `409` com `Não é possível excluir veículo com permanências registradas`. Não existe regra adicional no service que diferencie permanência aberta de finalizada: ambas impedem a exclusão.

## Inconsistências/limitações

- O cadastro exige `clienteId`, mas não confirma previamente o cliente e expõe a falha da FK como erro de banco.
- Não há validação de formato, case ou normalização de placa no backend (a interface converte o texto para maiúsculas).
- É possível alterar o cliente de um veículo sem verificação funcional adicional; a FK é a única proteção.

## Fonte

`VeiculoController`, `VeiculoRepository`, modelo `Veiculo` e tabelas `veiculos`/`permanencias` em `database/init.sql`.
