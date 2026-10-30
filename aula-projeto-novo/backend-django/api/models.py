from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "clientes"


class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    cor = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="veiculos")

    class Meta:
        db_table = "veiculos"


class Vaga(models.Model):
    class Tipo(models.TextChoices):
        CARRO = "CARRO"
        MOTO = "MOTO"

    class Status(models.TextChoices):
        LIVRE = "LIVRE"
        OCUPADA = "OCUPADA"

    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=5, choices=Tipo.choices)
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.LIVRE)

    class Meta:
        db_table = "vagas"


class Permanencia(models.Model):
    class Status(models.TextChoices):
        ABERTO = "ABERTO"
        FINALIZADO = "FINALIZADO"

    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name="permanencias")
    vaga = models.ForeignKey(Vaga, on_delete=models.PROTECT, related_name="permanencias")
    data_hora_entrada = models.DateTimeField(auto_now_add=True)
    data_hora_saida = models.DateTimeField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABERTO)

    class Meta:
        db_table = "permanencias"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["veiculo"]),
            models.Index(fields=["vaga"]),
        ]
