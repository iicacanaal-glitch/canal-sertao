from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# ---------------------
# Usuários com grupos
# ---------------------
class User(AbstractUser):
    GRUPOS_CHOICES = [
        ('seinfra', 'SEINFRA'),
        ('casal', 'CASAL'),
        ('segov', 'SEGOV'),
        ('seagri', 'SEAGRI'),
        ('arsal', 'ARSAL'),
        ('sefaz', 'SEFAZ'),
        ('iica', 'IICA'),
    ]

    grupo = models.CharField(max_length=50, choices=GRUPOS_CHOICES, blank=True, null=True)
    email = models.EmailField()

    # Evita conflito de acessores reversos com auth.User.
    groups = models.ManyToManyField(Group, related_name="+", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="+", blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Municipio(models.Model):
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"


class Irrigantes(models.Model):
    nome = models.CharField(max_length=255)
    apelido = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    estado_civil = models.CharField(max_length=50)
    nome_mae = models.CharField(max_length=255)
    data_nascimento = models.DateField()

    conjuge = models.CharField(max_length=255, blank=True, null=True)
    cpf_conjuge = models.CharField(max_length=14, blank=True, null=True)
    rg_conjuge = models.CharField(max_length=20, blank=True, null=True)
    estado_civil_conjuge = models.CharField(max_length=50, blank=True, null=True)

    telefone = models.CharField(max_length=20)

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        related_name='irrigantes'
    )

    finalidade = models.TextField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    nome_imovel = models.CharField(max_length=255)
    comunidade = models.CharField(max_length=255, blank=True, null=True)

    area_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Em tarefas")
    area_irrigada = models.DecimalField(max_digits=10, decimal_places=2)

    forma_ocupacao = models.CharField(max_length=100)
    permissao_de_uso = models.CharField(max_length=100, blank=True, null=True)
    num_permissao = models.CharField(max_length=100, blank=True, null=True)

    uso_individual = models.BooleanField(default=False)
    uso_coletivo = models.BooleanField(default=False)
    quant_coletivo = models.IntegerField(blank=True, null=True)

    num_lacre = models.CharField(max_length=100, blank=True, null=True)
    trecho_captacao = models.CharField(max_length=255, blank=True, null=True)

    vazao_requerida = models.DecimalField(max_digits=10, decimal_places=2, help_text="m³/h")
    potencia_bomba = models.DecimalField(max_digits=10, decimal_places=2, help_text="cv")

    dias_uso_por_semana = models.IntegerField()

    diametro_succao = models.DecimalField(max_digits=10, decimal_places=2)
    diametro_recalque = models.DecimalField(max_digits=10, decimal_places=2)

    energia_utilizada = models.CharField(max_length=100)
    vazao_bombeamento = models.DecimalField(max_digits=10, decimal_places=2)
    distancia_captacao_destinacao = models.DecimalField(max_digits=10, decimal_places=2)
    destinacao_apos_captacao = models.TextField()

    uso_direto = models.BooleanField(default=False)
    uso_reservatorio = models.BooleanField(default=False)
    vol_reservatorio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    altura_recalque = models.DecimalField(max_digits=10, decimal_places=2)

    termo_autorizacao_semarh = models.FileField(upload_to='termos/', blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    cadastrante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='irrigantes_cadastrados'
    )

    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class Parada(models.Model):
    TIPO_CHOICES = [
        ('emergencial', 'Emergencial'),
        ('programada', 'Programada'),
    ]

    STATUS_CHOICES = [
        ('em_atividade', 'Em atividade'),
        ('encerrada', 'Encerrada'),
        ('cancelada', 'Cancelada'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=255)
    motivo = models.TextField()

    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(blank=True, null=True)

    municipios_afetados = models.ManyToManyField(
        Municipio,
        related_name='paradas'
    )

    responsavel = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='em_atividade'
    )

    observacoes = models.TextField(blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    cadastrante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='paradas_cadastradas'
    )

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


#Arquivos e Documentos
class CategoriaDocumento(models.Model):
    nome = models.CharField(max_length=255)
    pai = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Documento(models.Model):
    titulo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='documentos/')
    descricao = models.TextField(blank=True, null=True)

    categoria = models.ForeignKey(
        CategoriaDocumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    data_upload = models.DateTimeField(auto_now_add=True)

    cadastrante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.titulo
