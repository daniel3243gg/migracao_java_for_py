# Schema do banco de dados

Mapeamento do schema efetivamente usado pelo `aula-projeto-legado`. O banco é PostgreSQL 15, criado pelo [`database/init.sql`](../../aula-projeto-legado/database/init.sql) na primeira inicialização do container. O arquivo [`backend/src/main/resources/schema.sql`](../../aula-projeto-legado/backend/src/main/resources/schema.sql) é uma cópia documental do DDL, não o script executado pelo container.

## Configuração do banco

| Propriedade | Valor no Docker Compose |
|---|---|
| SGBD | PostgreSQL 15 Alpine |
| Banco | `estacionamento` |
| Usuário | `postgres` |
| Porta publicada | `5432` |
| Volume | `postgres_data` |

As credenciais estão declaradas no `docker-compose.yml` do legado. O script de inicialização é montado como somente leitura em `/docker-entrypoint-initdb.d/init.sql` e só é executado pelo PostgreSQL na criação inicial do volume.

## Modelo relacional

```text
clientes (1) ──────────────── (N) veiculos
                                      │
                                      │ (1)
                                      │
                                      └──────── (N) permanencias (N) ──────── (1) vagas
```

Cardinalidades permitidas pelo schema:

- um cliente pode ter vários veículos;
- cada veículo pertence a exatamente um cliente;
- um veículo pode ter várias permanências históricas;
- uma permanência referencia exatamente um veículo e uma vaga;
- uma vaga pode ser referenciada por várias permanências ao longo do tempo.

O banco não possui constraint que impeça duas permanências `ABERTO` para o mesmo veículo ou para a mesma vaga. Essa proteção é feita parcialmente pelo service e pelo status da vaga.

## Tabelas

### `clientes`

| Coluna | Tipo | Nulo | Default | Regras |
|---|---|---:|---|---|
| `id` | `BIGSERIAL` | não | sequência | `PRIMARY KEY` |
| `nome` | `VARCHAR(100)` | não | — | — |
| `cpf` | `VARCHAR(14)` | não | — | `UNIQUE` |
| `telefone` | `VARCHAR(20)` | sim | `NULL` | — |
| `email` | `VARCHAR(100)` | sim | `NULL` | — |

O banco garante apenas presença e unicidade de `cpf`; não valida formato de CPF, telefone ou email.

### `veiculos`

| Coluna | Tipo | Nulo | Default | Regras |
|---|---|---:|---|---|
| `id` | `BIGSERIAL` | não | sequência | `PRIMARY KEY` |
| `placa` | `VARCHAR(10)` | não | — | `UNIQUE` |
| `marca` | `VARCHAR(50)` | não | — | — |
| `modelo` | `VARCHAR(50)` | não | — | — |
| `cor` | `VARCHAR(30)` | não | — | — |
| `cliente_id` | `BIGINT` | não | — | FK para `clientes(id)` com `ON DELETE CASCADE` |

O banco não valida formato, case ou composição da placa. A aplicação exige um `clienteId`, mas a existência do cliente é garantida apenas pela FK.

### `vagas`

| Coluna | Tipo | Nulo | Default | Regras |
|---|---|---:|---|---|
| `id` | `BIGSERIAL` | não | sequência | `PRIMARY KEY` |
| `numero` | `VARCHAR(10)` | não | — | `UNIQUE` |
| `tipo` | `VARCHAR(5)` | não | — | `CHECK (tipo IN ('CARRO', 'MOTO'))` |
| `status` | `VARCHAR(7)` | não | `'LIVRE'` | `CHECK (status IN ('LIVRE', 'OCUPADA'))` |

Não existe FK ou outra constraint relacionando `tipo` ao veículo. O banco também não sabe se `status = 'OCUPADA'` corresponde a uma permanência aberta.

### `permanencias`

| Coluna | Tipo | Nulo | Default | Regras |
|---|---|---:|---|---|
| `id` | `BIGSERIAL` | não | sequência | `PRIMARY KEY` |
| `veiculo_id` | `BIGINT` | não | — | FK para `veiculos(id)`, sem cascata |
| `vaga_id` | `BIGINT` | não | — | FK para `vagas(id)`, sem cascata |
| `data_hora_entrada` | `TIMESTAMP` | não | `CURRENT_TIMESTAMP` | — |
| `data_hora_saida` | `TIMESTAMP` | sim | `NULL` | — |
| `valor_total` | `DECIMAL(10,2)` | sim | `NULL` | — |
| `status` | `VARCHAR(10)` | não | `'ABERTO'` | `CHECK (status IN ('ABERTO', 'FINALIZADO'))` |

`TIMESTAMP` não inclui informação de fuso horário. O cálculo da tarifa e a transição de estado são feitos pela aplicação; o banco não exige, por exemplo, saída para uma permanência finalizada nem impede valor nulo em qualquer estado.

## Chaves e efeitos de exclusão

| Origem | Referência | Efeito ao excluir o pai |
|---|---|---|
| `veiculos.cliente_id` | `clientes.id` | `CASCADE`: remove os veículos do cliente, se as dependências posteriores permitirem |
| `permanencias.veiculo_id` | `veiculos.id` | Sem cascata: permanências impedem a exclusão do veículo |
| `permanencias.vaga_id` | `vagas.id` | Sem cascata: permanências impedem a exclusão da vaga |

Isso produz um caso importante: um cliente pode ser excluído com seus veículos quando eles não possuem permanências; se possuírem, a cascata é barrada pela FK de `permanencias`.

## Índices

Além dos índices implícitos de chaves primárias e unicidades, o `init.sql` cria:

| Índice | Tabela/coluna | Finalidade provável |
|---|---|---|
| `idx_permanencias_status` | `permanencias(status)` | filtros por status e indicadores |
| `idx_permanencias_veiculo_id` | `permanencias(veiculo_id)` | busca de permanência aberta e histórico do veículo |
| `idx_permanencias_vaga_id` | `permanencias(vaga_id)` | consultas e integridade por vaga |
| `idx_veiculos_cliente_id` | `veiculos(cliente_id)` | relacionamento/listagem por cliente |

Os índices são criados com `IF NOT EXISTS`. Não há índice parcial ou `UNIQUE` para permanência aberta.

## Dados iniciais

Na inicialização são inseridas 15 vagas, usando `ON CONFLICT (numero) DO NOTHING`:

- `A01` a `A10`, tipo `CARRO`;
- `B01` a `B05`, tipo `MOTO`.

Como o status não é informado no `INSERT`, todas começam com o default `LIVRE`. Não são inseridos clientes, veículos ou permanências iniciais.

## Garantias do banco versus aplicação

### Garantido pelo banco

- IDs gerados e chaves primárias;
- campos obrigatórios definidos como `NOT NULL`;
- unicidade de CPF, placa e número da vaga;
- tipos e estados permitidos por `CHECK`;
- existência de cliente, veículo e vaga referenciados por FKs;
- cascata de cliente para veículo;
- bloqueio de exclusão de veículo/vaga com permanências.

### Não garantido pelo banco

- existência prévia do veículo antes da tentativa de entrada, com erro de domínio amigável;
- uma única permanência aberta por veículo ou vaga;
- correspondência entre tipo de veículo e tipo de vaga;
- coerência entre status de vaga e permanências abertas;
- transição válida entre `ABERTO` e `FINALIZADO`;
- preenchimento coerente de saída e valor;
- cálculo da tarifa de R$ 5,00 por hora.

Essas regras dependem dos controllers e do `PermanenciaService`, e algumas podem ser contornadas por alteração direta da vaga ou pelo próprio banco.

## Fontes

- [`database/init.sql`](../../aula-projeto-legado/database/init.sql) — DDL executado e seeds;
- [`backend/src/main/resources/schema.sql`](../../aula-projeto-legado/backend/src/main/resources/schema.sql) — cópia documental do DDL;
- [`PermanenciaService.java`](../../aula-projeto-legado/backend/src/main/java/com/estacionamento/service/PermanenciaService.java) — transações e regras de entrada/saída;
- repositórios em `backend/src/main/java/com/estacionamento/repository/` — consultas e persistência.
