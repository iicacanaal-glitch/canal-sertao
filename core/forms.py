from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Parada, Municipio, Irrigantes, Documento, CategoriaDocumento, Projeto

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ParadaForm(forms.ModelForm):
    class Meta:
        model = Parada
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'municipios_afetados': forms.CheckboxSelectMultiple(),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['municipios_afetados'].queryset = Municipio.objects.filter(ativo=True).order_by('nome')


class IrrigantesForm(forms.ModelForm):

    class Meta:
        model = Irrigantes
        fields = '__all__'
        widgets = {
            # Dados pessoais
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'apelido': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            # Cônjuge
            'conjuge': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_conjuge': forms.TextInput(attrs={'class': 'form-control'}),
            'rg_conjuge': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_civil_conjuge': forms.TextInput(attrs={'class': 'form-control'}),

            # Contato
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),

            # Localização
            'municipio': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),

            # Imóvel
            'nome_imovel': forms.TextInput(attrs={'class': 'form-control'}),
            'comunidade': forms.TextInput(attrs={'class': 'form-control'}),
            'finalidade': forms.Textarea(attrs={'class': 'form-control'}),

            # Área
            'area_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_irrigada': forms.NumberInput(attrs={'class': 'form-control'}),

            # Uso
            'forma_ocupacao': forms.TextInput(attrs={'class': 'form-control'}),
            'permissao_de_uso': forms.TextInput(attrs={'class': 'form-control'}),
            'num_permissao': forms.TextInput(attrs={'class': 'form-control'}),

            'uso_individual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'uso_coletivo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quant_coletivo': forms.NumberInput(attrs={'class': 'form-control'}),

            # Captação
            'num_lacre': forms.TextInput(attrs={'class': 'form-control'}),
            'trecho_captacao': forms.TextInput(attrs={'class': 'form-control'}),

            # Dados técnicos
            'vazao_requerida': forms.NumberInput(attrs={'class': 'form-control'}),
            'potencia_bomba': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_uso_por_semana': forms.NumberInput(attrs={'class': 'form-control'}),

            'diametro_succao': forms.NumberInput(attrs={'class': 'form-control'}),
            'diametro_recalque': forms.NumberInput(attrs={'class': 'form-control'}),

            'energia_utilizada': forms.TextInput(attrs={'class': 'form-control'}),
            'vazao_bombeamento': forms.NumberInput(attrs={'class': 'form-control'}),
            'distancia_captacao_destinacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'destinacao_apos_captacao': forms.Textarea(attrs={'class': 'form-control'}),

            # Reservatório
            'uso_direto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'uso_reservatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vol_reservatorio': forms.NumberInput(attrs={'class': 'form-control'}),
            'altura_recalque': forms.NumberInput(attrs={'class': 'form-control'}),

            # Arquivo
            'termo_autorizacao_semarh': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['municipio'].queryset = Municipio.objects.filter(ativo=True).order_by('nome')

        for field in self.fields:
            if self.errors.get(field):
                self.fields[field].widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()

        uso_reservatorio = cleaned_data.get("uso_reservatorio")
        vol_reservatorio = cleaned_data.get("vol_reservatorio")

        uso_coletivo = cleaned_data.get("uso_coletivo")
        quant_coletivo = cleaned_data.get("quant_coletivo")

        if uso_reservatorio and not vol_reservatorio:
            self.add_error('vol_reservatorio', 'Informe o volume do reservatório.')

        if uso_coletivo and not quant_coletivo:
            self.add_error('quant_coletivo', 'Informe a quantidade de usuários.')

        return cleaned_data


class CategoriaDocumentoForm(forms.ModelForm):
    class Meta:
        model = CategoriaDocumento
        fields = ['nome', 'descricao']

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição (opcional)'
            }),
        }


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            'titulo',
            'descricao',
            'arquivo',
            'categoria',
        ]

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do documento'
            }),

            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição (opcional)'
            }),

            'arquivo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')

        if arquivo:
            # Limite de 50MB
            if arquivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError("O arquivo deve ter no máximo 50MB.")

        return arquivo


class ProjetoForm(forms.ModelForm):

    class Meta:
        model = Projeto
        exclude = ['resultado', 'data_de_cadastro', 'cadastrante']

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do projeto',
                'required': True
            }),

            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva o projeto'
            }),

            'determinacao_legal': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'impacto_metas': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'alinhamento': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'situacao': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'dispo_recurso': forms.Select(attrs={'class': 'form-select', 'required': True}),

            'complexidade': forms.Select(attrs={'class': 'form-select'}),
            'custo': forms.Select(attrs={'class': 'form-select'}),
            'prazo': forms.Select(attrs={'class': 'form-select'}),
            'riscos': forms.Select(attrs={'class': 'form-select'}),
            'tempo_resultado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        campos_obrigatorios = [
            'determinacao_legal',
            'impacto_metas',
            'alinhamento',
            'situacao',
            'dispo_recurso',
            'complexidade',
            'custo',
            'prazo',
            'riscos',
            'tempo_resultado'
        ]

        for campo in campos_obrigatorios:
            if cleaned_data.get(campo) is None:
                self.add_error(campo, "Este campo é obrigatório.")

        return cleaned_data
