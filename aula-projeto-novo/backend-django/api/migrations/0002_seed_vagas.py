
from django.db import migrations

VAGAS_INICIAIS = (
    [(f"A{n:02d}", "CARRO") for n in range(1, 11)]
    + [(f"B{n:02d}", "MOTO") for n in range(1, 6)]
)


def criar_vagas_iniciais(apps, schema_editor):
    """Cria as 15 vagas iniciais sem duplicar nem sobrescrever.

    get_or_create reproduz o ON CONFLICT (numero) DO NOTHING do legado: se já
    existir vaga com o mesmo número, ela fica como está.
    """
    Vaga = apps.get_model("api", "Vaga")
    for numero, tipo in VAGAS_INICIAIS:
        Vaga.objects.get_or_create(numero=numero, defaults={"tipo": tipo, "status": "LIVRE"})


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_vagas_iniciais, migrations.RunPython.noop),
    ]
