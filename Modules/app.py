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

    if numeros.nostartswith("55"):
        numeros = "55" + numeros
                
    return numeros

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
    icon=ft.icons.UPLOAD_FILE,
)

executar_button = ft.ElevatedButton(
    "Executar",
    icon=ft.icons.PLAY_CIRCLE_FILLED
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
    label="Mensagens (separadas por '|')",
    value="|".join(textos),
    width=500,
    multiline=True,
    max_lines=10
)

# Status inicial.
status = ft.Text("Esperando planilha disparos...", text_align=ft.TextAlign.CENTER)

# Tela principal.
def main_page():
    return ft.View(
        "/main",
        controls=[
            ft.Column(
                [
                    # Texto do título.
                    ft.Row(
                        [titulo_text],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=50),
                    # Seção de configurações
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Configurações de Envio:", weight=ft.FontWeight.BOLD),
                                    ft.Row([delay_min_field, delay_max_field]),
                                    ft.Row([delay_min_contador_field, delay_max_contador_field]),
                                    contador_field,
                                    mensagens_field
                                ],
                                spacing=10
                            ),
                            padding=20,
                            width=600
                        )
                    ),
                    # Faixa dos botões.
                    ft.Row(
                        [upload_button, executar_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=26),
                    # Card com informações.
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Status:"),  # Rótulo "Status"
                                    status,  # Texto de status centralizado
                                ]
                            ),
                            width=500,
                            padding=10,
                        )
                    ),
                    ft.Container(height=200),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ]
    )

# Função principal para gerenciar as views.
def main(page: ft.Page):

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
                planilha = pd.ExcelFile(file_path)
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

            status.value = "Processando arquivo..."
            status.update()
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
            wp.envio_em_massa(planilha, textos, DELAY_MIN, DELAY_MAX, DELAY_MINCONTADOR, DELAY_MAXCONTADOR, CONTADOR)

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
        allowed_extensions = ["xlsx", "xls"]
        )
    executar_button.on_click = execute_file

    # Configurando a página inicial.
    page.overlay.append(file_picker)
    page.views.append(main_page())
    page.update()

ft.app(target=main)
