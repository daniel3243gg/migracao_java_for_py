"""Serialização manual dos models (Tarefa 4 do roteiro).

Chaves em camelCase, iguais ao JSON que o Gson gerava no backend Java.
Quem consulta veículos ou permanências deve usar select_related para evitar N+1.
"""


def _data(valor):
    # LocalDateTime em ISO 8601 sem fuso, como o JsonUtil do legado.
    return valor.isoformat() if valor is not None else None


def cliente_to_dict(cliente):
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "telefone": cliente.telefone,
        "email": cliente.email,
    }


def veiculo_to_dict(veiculo):
    return {
        "id": veiculo.id,
        "placa": veiculo.placa,
        "marca": veiculo.marca,
        "modelo": veiculo.modelo,
        "cor": veiculo.cor,
        "clienteId": veiculo.cliente_id,
        "clienteNome": veiculo.cliente.nome,
    }


def vaga_to_dict(vaga):
    return {
        "id": vaga.id,
        "numero": vaga.numero,
        "tipo": vaga.tipo,
        "status": vaga.status,
    }


def permanencia_to_dict(permanencia):
    valor = permanencia.valor_total
    return {
        "id": permanencia.id,
        "veiculoId": permanencia.veiculo_id,
        "veiculoPlaca": permanencia.veiculo.placa,
        "veiculoModelo": permanencia.veiculo.modelo,
        "vagaId": permanencia.vaga_id,
        "vagaNumero": permanencia.vaga.numero,
        "dataHoraEntrada": _data(permanencia.data_hora_entrada),
        "dataHoraSaida": _data(permanencia.data_hora_saida),
        # O contrato do legado é número JSON. O cálculo continua em Decimal no
        # serviço; a conversão acontece só aqui, na saída.
        "valorTotal": float(valor) if valor is not None else None,
        "status": permanencia.status,
    }
