# Indicadores

O dashboard calcula os indicadores diretamente no banco, por `GET /api/dashboard`.

| Indicador | Regra efetiva |
|---|---|
| `totalVagas` | Conta todas as linhas de `vagas`. |
| `vagasLivres` | Conta vagas cujo status é `LIVRE`. |
| `vagasOcupadas` | Conta vagas cujo status é `OCUPADA`. |
| `veiculosEstacionados` | Conta permanências com status `ABERTO`. |

Os três indicadores de vagas refletem o campo de status, não a existência real de permanências. Por isso, alterações manuais de status podem fazer `vagasOcupadas`/`vagasLivres` divergir de `veiculosEstacionados`. O dashboard não verifica compatibilidade de tipo, nem soma permanências finalizadas, valores ou receita.

Se não houver linhas, os `SUM(CASE...)` são lidos pelo JDBC como zero via `getLong`; o retorno é um objeto com chaves `totalVagas`, `vagasLivres`, `vagasOcupadas` e `veiculosEstacionados`. O controller aceita apenas `GET`; demais métodos retornam `405`.

## Fonte

`DashboardController.getDashboardData()` e tabela `vagas`/`permanencias` em `database/init.sql`.
