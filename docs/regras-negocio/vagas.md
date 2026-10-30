# Vagas

## Cadastro

**Condição.** `numero` deve ser informado e não vazio; `tipo` deve ser exatamente `CARRO` ou `MOTO`.

**Comportamento.** O número é único. A criação sempre grava status `LIVRE`, ignorando qualquer status enviado no payload, e retorna `201`. Número repetido retorna `409` com `Número de vaga já cadastrado`.

O banco reforça `numero` e `tipo` como não nulos, a unicidade do número e os valores permitidos de tipo/status. Não há regra de formato do número.

## Status, ocupação e liberação

Os estados válidos são `LIVRE` e `OCUPADA`. Na entrada de permanência, uma vaga livre passa para `OCUPADA`; na saída, passa para `LIVRE`. A troca desses estados ocorre na mesma transação da permanência.

O cadastro e a interface de edição permitem informar status, e a atualização grava diretamente `numero`, `tipo` e `status`. Se o status enviado na alteração for nulo ou inválido, o controller o substitui por `LIVRE`. Portanto, a alteração manual pode marcar uma vaga como ocupada ou livre sem criar/remover uma permanência.

**Inconsistência/limitação.** Não há bloqueio funcional para alterar uma vaga ocupada para livre, nem para apagar uma vaga marcada como ocupada quando não existe permanência referenciando-a. Isso pode fazer o status divergir das permanências. A integridade transacional protege as operações de entrada/saída, mas não as alterações administrativas.

## Exclusão e consulta

ID inexistente retorna `404`. Uma vaga referenciada por permanência não pode ser apagada, pois a FK `permanencias.vaga_id` não tem cascata; o controller responde `409` com `Não é possível excluir vaga com permanências registradas`. Vaga sem permanência pode ser excluída, inclusive se estiver com status `OCUPADA`.

Listagens podem filtrar por qualquer texto de status recebido na query; não há validação do filtro no controller. O banco só pode conter os dois valores válidos.

## Compatibilidade de tipo

O sistema não verifica se o tipo do veículo é compatível com o tipo da vaga. Além disso, o modelo de veículo não possui campo de tipo, apenas placa, marca, modelo e cor. A seleção da interface exibe o tipo da vaga, mas isso é apenas apresentação.

## Fonte

`VagaController`, `VagaRepository`, modelo `Vaga`, `PermanenciaService` e tabela `vagas` em `database/init.sql`.
