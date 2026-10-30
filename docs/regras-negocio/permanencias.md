# Permanências

## Estados e ciclo de vida

Uma permanência nasce em `ABERTO`, com `data_hora_entrada` e sem saída/valor. A saída muda o registro para `FINALIZADO`, grava `data_hora_saida` e `valor_total`, e libera a vaga. O banco restringe `status` a esses dois valores.

Não há endpoint de criação/alteração arbitrária: entrada é `POST /api/permanencias/entrada`, saída é `PUT /api/permanencias/{id}/saida`. Listagens podem filtrar por status.

## Entrada

**Condição.** O corpo deve possuir `veiculoId` e `vagaId`. O service verifica se o veículo já tem permanência `ABERTO`; se tiver, bloqueia com `409` e `Veículo já possui uma permanência em aberto.`

Em seguida, dentro de transação, a vaga é buscada com `SELECT ... FOR UPDATE`. Vaga inexistente gera `404` com `Vaga não encontrada.`; vaga `OCUPADA` gera `409` com `Vaga já está ocupada.`. Se livre, ela é marcada como `OCUPADA` e uma permanência aberta é inserida. O commit confirma as duas alterações e a entrada retorna `201`.

**Efeitos.** Cria relação veículo-vaga, registra `data_hora_entrada` no horário atual e altera status da vaga. A existência do veículo não é consultada explicitamente antes dessas etapas; se o ID não existir, o `INSERT` viola a FK, a transação sofre rollback e o erro normalmente aparece como `500`.

**Integridade e concorrência.** O `setAutoCommit(false)`, o `SELECT FOR UPDATE` da vaga e o rollback em qualquer exceção garantem que a ocupação e a permanência não sejam confirmadas separadamente. A checagem de permanência aberta do veículo não usa bloqueio de linha específico; a consistência adicional depende da sequência transacional e não existe índice/constraint SQL que imponha uma única permanência aberta por veículo.

## Saída

**Condição.** O ID deve identificar uma permanência existente. O service carrega o registro com `SELECT ... FOR UPDATE`; se não existir, gera `404` com `Permanência não encontrada.`. Se já estiver `FINALIZADO`, gera `409` com `Permanência já foi finalizada.`.

Para uma permanência aberta, registra o horário atual, calcula o valor, atualiza a permanência para `FINALIZADO` e marca a vaga como `LIVRE`, tudo na mesma transação. O resultado retornado contém a saída, o valor e o novo status (`200`).

## Cálculo da tarifa

A tarifa é de **R$ 5,00 por hora**. O service calcula `ChronoUnit.MINUTES.between(entrada, saída)`, arredonda frações de hora para cima com `(minutos + 59) / 60` e aplica mínimo de uma hora. Assim, qualquer duração de até 59 minutos inteiros custa R$ 5,00; 60 minutos custa R$ 5,00; 61 a 120 minutos custa R$ 10,00.

**Inconsistência/limitação.** O cálculo descarta segundos e nanossegundos antes do arredondamento. Uma duração real pouco acima de uma hora pode ser tratada como exatamente 60 minutos se a diferença inteira em minutos ainda for 60. Não há cálculo de tarifa negativa ou validação de datas no fluxo, pois os horários são gerados pelo próprio service.

## Relacionamentos e exclusões

As FKs de veículo e vaga em permanências não têm `ON DELETE CASCADE`; qualquer permanência, aberta ou finalizada, impede apagar o veículo ou a vaga. O service não faz exclusões e não corrige registros eventualmente divergentes criados por alteração manual do status da vaga.

## Consulta

Listagens são ordenadas pela entrada mais recente e podem filtrar por `ABERTO` ou `FINALIZADO` — o repositório aceita o texto do filtro e o banco limita os valores existentes. A consulta por ID retorna a permanência quando encontrada.

**Inconsistência/limitação.** No `PermanenciaController`, quando a consulta por ID não encontra registro, o método não envia resposta. O fluxo não converte esse caso em `404`, embora o service de saída trate corretamente a mesma ausência como `Permanência não encontrada.`.

## Fonte

`PermanenciaController`, `PermanenciaService`, `PermanenciaRepository`, modelo `Permanencia` e tabela `permanencias` em `database/init.sql`.
