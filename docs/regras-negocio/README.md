# Regras de negócio do `aula-projeto-legado`

Esta documentação descreve o comportamento efetivamente implementado no legado, com base nos controllers, repositórios, service e schema SQL. Ela registra tanto as regras pretendidas pelo fluxo quanto as restrições reais do banco e as inconsistências observadas. Não é uma especificação de uma futura implementação.

## Domínio

- **Cliente** identifica a pessoa responsável por um ou mais veículos.
- **Veículo** pertence a um cliente e pode ter permanências no estacionamento.
- **Vaga** possui número, tipo (`CARRO` ou `MOTO`) e status (`LIVRE` ou `OCUPADA`).
- **Permanência** relaciona veículo e vaga, começando como `ABERTO` e terminando como `FINALIZADO`.

O fluxo principal é:

```text
Cliente 1 ─── N Veículo 1 ─── N Permanência N ─── 1 Vaga
                                  │                    │
                                  └─ ABERTO ocupa ─────┘
                                  └─ FINALIZADO libera
```

O cadastro de veículo exige um cliente existente por chave estrangeira. A entrada verifica se o veículo não tem outra permanência aberta, bloqueia a vaga, exige vaga livre, marca-a como ocupada e cria a permanência na mesma transação. A saída finaliza a permanência, calcula o valor e libera a vaga na mesma transação.

## Fontes e convenções

As fontes principais são:

- `aula-projeto-legado/database/init.sql` — schema executado e dados iniciais;
- `aula-projeto-legado/backend/src/main/resources/schema.sql` — cópia documental do schema;
- `backend/src/main/java/com/estacionamento/controller/` — validações e respostas HTTP;
- `backend/src/main/java/com/estacionamento/service/PermanenciaService.java` — regras transacionais de entrada e saída;
- `backend/src/main/java/com/estacionamento/repository/` — consultas, relacionamentos e efeitos persistidos.

Quando controller, service e banco divergem, a regra descrita como efetiva considera o resultado combinado da execução, incluindo a restrição do banco. Essas situações aparecem como **Inconsistência/limitação**.

## Documentos por domínio

- [Contrato OpenAPI da API](../api/openapi.yaml)
- [Mapeamento do schema do banco](../db/README.md)
- [Clientes](clientes.md)
- [Veículos](veiculos.md)
- [Vagas](vagas.md)
- [Permanências](permanencias.md)
- [Indicadores](indicadores.md)
