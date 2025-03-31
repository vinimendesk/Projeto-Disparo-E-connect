'''
    ========== APLICAÇÃO PRINCIPAL ==========
'''

import flet as ft
import pandas as pd
import openpyxl
import whatsapp as wp


# Variável global que verifica se foi feito o upload do arquivo.
is_uploaded = False
# Variável que armazena a planilha lida.
global planilha
# Variável que armazena o caminho da planilha.
global file_path

# Parâmetros padrão.
DELAY_MIN = 120
DELAY_MAX = 250
DELAY_MINCONTADOR = 3600
DELAY_MAXCONTADOR = 5200
CONTADOR = 50
textos = ["Olá, (nome), tudo bem? \nEstou aqui para te ajudar com o que precisar. \nAtenciosamente, \nEquipe E-connect",]

# (Executar_button) Função remover o hífen e o 9, caso necessário.
def formatar_coluna(numeros):
    numeros = str(numeros)

    numeros = numeros.replace("-", "")

    if not numeros.startswith("55"):
        numeros = "55" + numeros
                
    return numeros

def processar_textos(texto_campo):
    """
    Processa o texto do campo separado por |, removendo apenas espaços extras indesejados,
    mas preservando quebras de linha e formatação intencional.
    """
    textos = []
    for texto in texto_campo.split("|"):
        # Remove espaços no início e final, mas preserva quebras de linha e espaços internos
        texto = texto.strip(' \t')  # Remove apenas espaços e tabs do início/fim
        if texto:  # Ignora strings vazias
            textos.append(texto)
    return textos

# Componentes.
# Título do app.
titulo_text = ft.Text(
    "DISPARADOR WHATSAPP",
    size=18,
    weight=ft.FontWeight.BOLD,
    font_family="Roboto",
    text_align=ft.TextAlign.CENTER
)

# Título do tutorial.
tutorial_text = ft.Text(
    "TUTORIAL",
    size=18,
    weight=ft.FontWeight.BOLD,
    font_family="Roboto",
    text_align=ft.TextAlign.CENTER
)

# Botões.
upload_button = ft.ElevatedButton(
    "Upload",
    icon=ft.Icons.UPLOAD_FILE,
)

executar_button = ft.ElevatedButton(
    "Executar",
    icon=ft.Icons.PLAY_CIRCLE
)

# UI Componets de parâmetros.

# Campos para os parâmetros
delay_min_field = ft.TextField(
    label="Delay mínimo entre mensagens (segundos)",
    value=str(DELAY_MIN),
    width=300,
    keyboard_type=ft.KeyboardType.NUMBER
)

delay_max_field = ft.TextField(
    label="Delay máximo entre mensagens (segundos)",
    value=str(DELAY_MAX),
    width=300,
    keyboard_type=ft.KeyboardType.NUMBER
)

delay_min_contador_field = ft.TextField(
    label="Delay mínimo após contador (segundos)",
    value=str(DELAY_MINCONTADOR),
    width=300,
    keyboard_type=ft.KeyboardType.NUMBER
)

delay_max_contador_field = ft.TextField(
    label="Delay máximo após contador (segundos)",
    value=str(DELAY_MAXCONTADOR),
    width=300,
    keyboard_type=ft.KeyboardType.NUMBER
)

contador_field = ft.TextField(
    label="Quantidade de mensagens antes da pausa",
    value=str(CONTADOR),
    width=300,
    keyboard_type=ft.KeyboardType.NUMBER
)

mensagens_field = ft.TextField(
    label="Mensagens (separadas por '|'). Coloque (nome) para substituir pelo nome do cliente.",
    value="|".join(textos),
    width=600,
    multiline=True,
    max_lines=None,
    expand=True
)

# Status inicial.
status = ft.Text("Esperando planilha disparos...", text_align=ft.TextAlign.CENTER)

# Tela principal.
def main_page():
    return ft.View(
        "/main",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Column(
                [
                    # Cabeçalho
                    ft.Row([titulo_text], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=20),
                    
                    # Área de configurações com largura fixa
                    ft.Container(
                        width=700,  # Largura fixa para alinhamento
                        content=ft.Column(
                            [
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("Configurações de Envio:", 
                                                       weight=ft.FontWeight.BOLD,
                                                       text_align=ft.TextAlign.CENTER),
                                                ft.Row(
                                                    [delay_min_field, delay_max_field],
                                                    alignment=ft.MainAxisAlignment.CENTER
                                                ),
                                                ft.Row(
                                                    [delay_min_contador_field, delay_max_contador_field],
                                                    alignment=ft.MainAxisAlignment.CENTER
                                                ),
                                                ft.Container(contador_field, alignment=ft.alignment.center),
                                                mensagens_field
                                            ],
                                            spacing=10,
                                            scroll=ft.ScrollMode.AUTO,
                                        ),
                                        padding=20,
                                    ),
                                ),
                            ],
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    
                    # Área de botões e status com a MESMA largura
                    ft.Container(
                        width=700,  # Mesma largura do card de configurações
                        content=ft.Column(
                            [
                                ft.Row(
                                    [upload_button, executar_button],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=50
                                ),
                                ft.Container(height=20),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("Status:", 
                                                       weight=ft.FontWeight.BOLD,
                                                       text_align=ft.TextAlign.CENTER),
                                                status,
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=20,
                                        alignment=ft.alignment.center,
                                    ),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
                expand=True,
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]
    )

# Função principal para gerenciar as views.
def main(page: ft.Page):

    page.title = "Disparador WhatsApp"
    page.window_width = 800
    page.window_height = 700
    page.window_min_width = 600
    page.window_min_height = 600
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Função para upload do arquivo.
    def upload_file_result(e: ft.FilePickerResultEvent):
        global is_uploaded
        global planilha
        global file_path
        # Se arquivo encontrado.
        if e.files:
            # Obtém o caminho do arquivo selecionado.
            file_path = e.files[0].path

            try:
                planilha = pd.read_csv(file_path)
                is_uploaded = True
                status.value = "Arquivo carregado com sucesso!"
                status.update()
            except Exception as err:
                status.value = f"Erro ao processar o arquivo: {err}"
                status.update()
    
    # Função para fazer a limpeza da planilha.
    def execute_file(e):
        global is_uploaded
        if is_uploaded:

            try:
                current_delay_min = int(delay_min_field.value)  
                current_delay_max = int(delay_max_field.value)
                current_delay_min_contador = int(delay_min_contador_field.value)
                current_delay_max_contador = int(delay_max_contador_field.value)
                current_contador = int(contador_field.value)
            except ValueError:
                status.value = "Valores inválidos para os delays ou contador!"

            status.value = "Processando arquivo..."
            status.update()
            # Verificar se as colunas necessárias existem
            if 'numero' not in planilha.columns or 'nome' not in planilha.columns:
                status.value = "Planilha deve conter colunas 'numero' e 'nome'"
                status.update()
                return

            textos = processar_textos(mensagens_field.value)

            # Verifica se há textos válidos
            if not textos:
                status.value = "Nenhuma mensagem válida encontrada!"
                status.update()
                return

            # Faz a formatação dos numeros.
            planilha["numero"] = planilha["numero"].apply(formatar_coluna)
            status.value = "Planilha formatada com sucesso!"
            status.update()

            status.value = "Faça login no whatsApp web com o QR Code."
            status.update()
            # Inicia o whatsapp e espera fazer o QR CODE.
            wp.abrir_whatsapp()
            status.value = "Login feito com sucesso!"
            status.update()

            status.value = "Enviando mensagens..."
            status.update()
            wp.envio_em_massa(
                planilha, 
                textos, 
                current_delay_min, 
                current_delay_max, 
                current_delay_min_contador, 
                current_delay_max_contador, 
                current_contador
                )

            status.value = "Planilha processada com sucesso!"
            status.update()

        else:
            status.value = "Faça upload da planilha primeiro."
            status.update()

    #Cria o FilePicker para selecionar os arquivos.
    file_picker = ft.FilePicker(on_result=upload_file_result)

    # Associando funções aos botões.
    upload_button.on_click = lambda e: file_picker.pick_files(
        allow_multiple = False,
        allowed_extensions = ["csv"]
        )
    executar_button.on_click = execute_file

    # Configurando a página inicial.
    page.overlay.append(file_picker)
    page.views.append(main_page())
    page.update()

ft.app(target=main)
