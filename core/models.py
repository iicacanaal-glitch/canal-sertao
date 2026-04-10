from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid


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
    horas_uso_por_dia = models.IntegerField(default=0)

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



class Projeto(models.Model):
    NOTA_CHOICES = [(i, i) for i in range(1, 6)]

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    determinacao_legal = models.IntegerField(choices=NOTA_CHOICES)
    impacto_metas = models.IntegerField(choices=NOTA_CHOICES)
    alinhamento = models.IntegerField(choices=NOTA_CHOICES)
    situacao = models.IntegerField(choices=NOTA_CHOICES)
    dispo_recurso = models.IntegerField(choices=NOTA_CHOICES)
    complexidade = models.IntegerField(choices=NOTA_CHOICES)
    custo = models.IntegerField(choices=NOTA_CHOICES)
    prazo = models.IntegerField(choices=NOTA_CHOICES)
    riscos = models.IntegerField(choices=NOTA_CHOICES)
    tempo_resultado = models.IntegerField(choices=NOTA_CHOICES)

    data_de_cadastro = models.DateTimeField(auto_now_add=True)
    cadastrante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    resultado = models.FloatField(blank=True, null=True)

    def calcular_resultado(self):
        return (
            self.determinacao_legal * 8 +
            self.impacto_metas * 7 +
            self.alinhamento * 7 +
            self.situacao * 5 +
            self.dispo_recurso * 8 +
            self.complexidade * -2 +
            self.custo * -3 +
            self.prazo * -1 +
            self.riscos * -4 +
            self.tempo_resultado * -2
        )

    def save(self, *args, **kwargs):
        self.resultado = self.calcular_resultado()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-resultado']

    def __str__(self):
        return self.nome


class Manifestacao(models.Model):
    TIPO_CHOICES = [
        ('denuncia', 'Denúncia'), #CASAL
        ('reclamacao', 'Reclamação'), #SEAGRI
        ('solicitacao', 'Solicitação'), #CASAL
        ('sugestao', 'Sugestão'), #SEAGRI
        ('elogio', 'Elogio'), #NÃO LEMBRO DE VER ALGUÉM ELOGIAR
    ]

    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('em_analise', 'Em análise'),
        ('encaminhado', 'Encaminhado'),
        ('em_andamento', 'Em andamento'),
        ('concluido', 'Concluído'),
    ]
    CLASSIFICACAO_CHOICES = [
        ('agropecuaria', 'Agropecuária'),
        ('consumo_humano', 'Consumo Humano'),
        ('outros', 'Outros'),
    ]

    nome = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    anonimo = models.BooleanField(default=False)
    classificacao = models.CharField(max_length=20, choices=CLASSIFICACAO_CHOICES, blank=True, null=True)

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    assunto = models.CharField(max_length=200)
    descricao = models.TextField()

    municipio = models.CharField(max_length=150, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    setor_responsavel = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='recebido'
    )

    anexo = models.FileField(
        upload_to='ouvidoria/',
        blank=True,
        null=True
    )

    protocolo = models.CharField(max_length=20, unique=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def gerar_protocolo(self):
        return str(uuid.uuid4())[:8].upper()

    def definir_setor(self):
        if self.classificacao == 'agropecuaria':
            return 'SEAGRI'
        elif self.classificacao in ['consumo_humano', 'outros']:
            return 'CASAL'

        return 'CASAL'

    def save(self, *args, **kwargs):

        if not self.protocolo:
            self.protocolo = self.gerar_protocolo()

        if not self.setor_responsavel:
            self.setor_responsavel = self.definir_setor()

        super().save(*args, **kwargs)

    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def cor_status(self):
        cores = {
            'recebido': 'secondary',
            'em_analise': 'info',
            'encaminhado': 'primary',
            'em_andamento': 'warning',
            'concluido': 'success',
            'indeferido': 'danger',
        }
        return cores.get(self.status, 'secondary')

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Manifestação"
        verbose_name_plural = "Manifestações"

    def __str__(self):
        return f"{self.protocolo} - {self.assunto}"


class ManifestacaoHistorico(models.Model):

    manifestacao = models.ForeignKey(
        Manifestacao,
        on_delete=models.CASCADE,
        related_name='historico'
    )

    status = models.CharField(
        max_length=20,
        choices=Manifestacao.STATUS_CHOICES
    )

    descricao = models.TextField(blank=True, null=True)

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manifestacao.protocolo} - {self.status}"
