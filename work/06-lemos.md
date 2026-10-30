# 06 — Lemos

## Responsabilidade

Implementar as regras de negócio de entrada e saída de veículos.

## Pré-requisito

Petry deve ter concluído Docker, CORS e integração, e Breno/Theo/Gabs devem ter concluído suas etapas.

## Tarefas

- [ ] Criar `api/services/permanencia_service.py`.
- [ ] Implementar `registrar_entrada(veiculo_id, vaga_id)`.
- [ ] Impedir nova permanência aberta para o mesmo veículo.
- [ ] Impedir entrada em vaga inexistente ou ocupada.
- [ ] Atualizar a vaga para `OCUPADA` e criar permanência `ABERTO`.
- [ ] Implementar `registrar_saida(permanencia_id)`.
- [ ] Impedir saída de permanência inexistente ou já finalizada.
- [ ] Calcular valor com tarifa de R$ 5,00, mínimo de uma hora e `math.ceil`.
- [ ] Usar `Decimal` no cálculo monetário.
- [ ] Criar as views de entrada, saída e listagem de permanências.
- [ ] Usar `select_related('veiculo', 'vaga')` na listagem.
- [ ] Retornar erros de negócio como HTTP 409 nas views.

## Entrega final

Fluxo de estacionamento completo funcionando localmente e em Docker, com entrada, saída, cálculo correto e validação final dos critérios de aceite.

## Status

- [ ] Não iniciado
