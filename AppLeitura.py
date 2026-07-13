import os
import sqlite3
import subprocess
import tempfile
import customtkinter as ctk

# Importações para a geração do PDF profissional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# =========================================================================
# CONFIGURAÇÃO DA PALETA DE CORES PERSONALIZADA
# =========================================================================
COR_AZUL_TEC = ("#0066FF", "#0078D4")       # Confiança / Elementos de Ação
COR_VERDE_INT = ("#107C41", "#00FFAD")      # Crescimento / Sucesso / Avaliação Sim
COR_GRAFITE = ("#333a3e", "#202528")        # Textos e fundos contrastantes
COR_GELO = ("#F8F9FA", "#1e1e24")           # Fundos principais de janelas e cards

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class AppLeituraCompleto(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerenciador de Leituras Anuais")
        self.geometry("700x780")  # Ligeiramente mais largo para acomodar o Dashboard
        self.resizable(False, False)

        self.configure(fg_color=COR_GELO)
        self.init_db()

        # --- Estrutura de Abas (Tabs) ---
        self.tabview = ctk.CTkTabview(
            self, 
            width=660, 
            height=740,
            segmented_button_selected_color=COR_AZUL_TEC[1],
            segmented_button_selected_hover_color=COR_AZUL_TEC[0],
            text_color=("#202528", "#F8F9FA")
        )
        self.tabview.pack(padx=20, pady=20)
        
        self.tab_cadastro = self.tabview.add("📝 Cadastrar Livro")
        self.tab_consulta = self.tabview.add("🔍 Consultar Biblioteca")
        self.tab_dashboard = self.tabview.add("📊 Dashboard")

        self.tab_cadastro.configure(fg_color=COR_GELO)
        self.tab_consulta.configure(fg_color=COR_GELO)
        self.tab_dashboard.configure(fg_color=COR_GELO)

        # Monta as interfaces
        self.montar_aba_cadastro()
        self.montar_aba_consulta()
        self.montar_aba_dashboard()

        # Renderização e buscas iniciais
        self.executar_busca()
        self.atualizar_dashboard()

    def init_db(self):
        self.conn = sqlite3.connect("biblioteca_pessoal.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT,
                categoria TEXT,
                ano_publicacao TEXT,
                avaliacao TEXT,
                resumo TEXT
            )
        """)
        self.conn.commit()

    # =========================================================================
    # ABA: CADASTRO
    # =========================================================================
    def montar_aba_cadastro(self):
        lbl = ctk.CTkLabel(self.tab_cadastro, text="Adicionar Nova Leitura", font=ctk.CTkFont(size=18, weight="bold"), text_color=COR_AZUL_TEC)
        lbl.pack(pady=(15, 20))

        input_args = {"width": 480, "border_color": ("#cccccc", "#444444")}

        self.entry_titulo = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Título do Livro", **input_args)
        self.entry_titulo.pack(pady=6)

        self.entry_autor = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Autor", **input_args)
        self.entry_autor.pack(pady=6)

        self.entry_categoria = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Categoria", **input_args)
        self.entry_categoria.pack(pady=6)

        self.entry_ano = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Ano de Publicação", **input_args)
        self.entry_ano.pack(pady=6)

        ctk.CTkLabel(self.tab_cadastro, text="Gostou da experiência de leitura?", font=ctk.CTkFont(size=12), text_color=COR_GRAFITE).pack(pady=(6, 2))
        self.combo_gostou = ctk.CTkComboBox(self.tab_cadastro, values=["Sim", "Não", "Mais ou menos"], width=480, button_color=COR_AZUL_TEC[1], border_color=COR_AZUL_TEC[1])
        self.combo_gostou.pack(pady=4)

        ctk.CTkLabel(self.tab_cadastro, text="Resumo da Obra (~20 linhas):", font=ctk.CTkFont(size=12), text_color=COR_GRAFITE).pack(pady=(6, 2))
        self.txt_resumo = ctk.CTkTextbox(self.tab_cadastro, width=480, height=200, activate_scrollbars=True, border_color=("#cccccc", "#444444"), border_width=1)
        self.txt_resumo.pack(pady=4)

        self.btn_salvar = ctk.CTkButton(self.tab_cadastro, text="Salvar Registro", command=self.salvar_livro, font=ctk.CTkFont(weight="bold"), width=200, fg_color=COR_AZUL_TEC[1], hover_color=COR_AZUL_TEC[0])
        self.btn_salvar.pack(pady=15)

    def salvar_livro(self):
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        categoria = self.entry_categoria.get().strip()
        ano = self.entry_ano.get().strip()
        avaliacao = self.combo_gostou.get()
        resumo = self.txt_resumo.get("1.0", "end-1c").strip()

        if not titulo:
            return

        self.cursor.execute("""
            INSERT INTO livros (titulo, autor, categoria, ano_publicacao, avaliacao, resumo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titulo, autor, categoria, ano, avaliacao, resumo))
        self.conn.commit()

        self.entry_titulo.delete(0, 'end')
        self.entry_autor.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')
        self.entry_ano.delete(0, 'end')
        self.txt_resumo.delete("1.0", "end")
        
        self.executar_busca()
        self.atualizar_dashboard()

    # =========================================================================
    # ABA: CONSULTA & FILTROS
    # =========================================================================
    def montar_aba_consulta(self):
        frame_filtros = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        frame_filtros.pack(pady=15, padx=15, fill="x")

        ctk.CTkLabel(frame_filtros, text="Buscar por:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COR_GRAFITE).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.combo_tipo_filtro = ctk.CTkComboBox(frame_filtros, values=["Todos", "Ano", "Categoria", "Autor"], width=120, button_color=COR_AZUL_TEC[1], border_color=COR_AZUL_TEC[1], command=self.gerenciar_estado_filtro)
        self.combo_tipo_filtro.grid(row=0, column=1, padx=5, pady=5)

        self.entry_busca = ctk.CTkEntry(frame_filtros, placeholder_text="Digite o termo...", width=240, border_color=("#cccccc", "#444444"))
        self.entry_busca.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_buscar = ctk.CTkButton(frame_filtros, text="🔍 Consultar", width=110, command=self.executar_busca, fg_color=COR_AZUL_TEC[1], hover_color=COR_AZUL_TEC[0])
        self.btn_buscar.grid(row=0, column=3, padx=5, pady=5)

        self.scroll_resultados = ctk.CTkScrollableFrame(self.tab_consulta, width=590, height=540, fg_color=("#eaeaea", "#16191b"))
        self.scroll_resultados.pack(pady=10, padx=15, fill="both", expand=True)

    def gerenciar_estado_filtro(self, escolha):
        if escolha == "Todos":
            self.entry_busca.delete(0, 'end')
            self.entry_busca.configure(state="disabled", placeholder_text="Mostrando tudo...")
        else:
            self.entry_busca.configure(state="normal", placeholder_text=f"Filtrar por {escolha}...")

    def executar_busca(self):
        for widget in self.scroll_resultados.winfo_children():
            widget.destroy()

        tipo = self.combo_tipo_filtro.get()
        termo = self.entry_busca.get().strip()

        if tipo == "Todos" or not termo:
            query = "SELECT titulo, autor, categoria, ano_publicacao, avaliacao, resumo FROM livros ORDER BY id DESC"
            parametros = ()
        else:
            colunas = {"Ano": "ano_publicacao", "Categoria": "categoria", "Autor": "autor"}
            query = f"SELECT titulo, autor, categoria, ano_publicacao, avaliacao, resumo FROM livros WHERE {colunas[tipo]} LIKE ? ORDER BY id DESC"
            parametros = (f"%{termo}%",)

        self.cursor.execute(query, parametros)
        livros = self.cursor.fetchall()

        if not livros:
            lbl_vazio = ctk.CTkLabel(self.scroll_resultados, text="Nenhum livro encontrado.", font=ctk.CTkFont(slant="italic"), text_color=COR_GRAFITE)
            lbl_vazio.pack(pady=40)
            return

        for livro in livros:
            titulo, autor, categoria, ano, avaliacao, resumo = livro

            card = ctk.CTkFrame(self.scroll_resultados, border_width=1, border_color=("#dbdbdb", "#2d3337"), fg_color=("#ffffff", "#202528"), corner_radius=10)
            card.pack(pady=8, padx=5, fill="x")

            # Grid interno para alinhar título e botão de impressão na mesma linha
            card.columnconfigure(0, weight=1)
            card.columnconfigure(1, weight=0)

            lbl_titulo = ctk.CTkLabel(card, text=f"📖 {titulo}", font=ctk.CTkFont(size=14, weight="bold"), text_color=("#202528", "#F8F9FA"), anchor="w")
            lbl_titulo.grid(row=0, column=0, pady=(10, 2), padx=15, sticky="ew")

            # Botão de Imprimir Resumo (PDF) localizado no canto superior direito do card
            btn_print = ctk.CTkButton(
                card, text="🖨️ Imprimir", width=80, height=24, font=ctk.CTkFont(size=11),
                fg_color="transparent", border_width=1, border_color=COR_AZUL_TEC[1], text_color=COR_AZUL_TEC,
                command=lambda t=titulo, a=autor, c=categoria, r=resumo: self.gerar_pdf_resumo(t, a, c, r)
            )
            btn_print.grid(row=0, column=1, pady=(10, 2), padx=15, sticky="e")

            meta_text = f"Por: {autor or 'Não informado'}  |  Cat: {categoria or 'Geral'}  |  Ano: {ano or '-'}"
            lbl_meta = ctk.CTkLabel(card, text=meta_text, font=ctk.CTkFont(size=11), text_color=("#707070", "#a0a0a0"), anchor="w")
            lbl_meta.grid(row=1, column=0, columnspan=2, pady=2, padx=15, sticky="ew")

            if avaliacao == "Sim":
                cor_txt = COR_VERDE_INT[1] if ctk.get_appearance_mode() == "Dark" else COR_VERDE_INT[0]
            elif avaliacao == "Não":
                cor_txt = "#e05c5c"
            else:
                cor_txt = "#ffb347"

            lbl_recomenda = ctk.CTkLabel(card, text=f"Curtiu? {avaliacao}", font=ctk.CTkFont(size=11, weight="bold"), text_color=cor_txt, anchor="w")
            lbl_recomenda.grid(row=2, column=0, columnspan=2, pady=2, padx=15, sticky="ew")

            if resumo:
                txt_box_resumo = ctk.CTkTextbox(card, height=80, activate_scrollbars=True, font=ctk.CTkFont(size=11), fg_color=("#f3f3f3", "#1a1e20"), text_color=("#202528", "#dcdcdc"))
                txt_box_resumo.insert("1.0", f"Resumo:\n{resumo}")
                txt_box_resumo.configure(state="disabled")
                txt_box_resumo.grid(row=3, column=0, columnspan=2, pady=(5, 10), padx=15, sticky="ew")

    # =========================================================================
    # ABA: DASHBOARD
    # =========================================================================
    def montar_aba_dashboard(self):
        # Título do Painel
        lbl = ctk.CTkLabel(self.tab_dashboard, text="Indicadores Globais de Leitura", font=ctk.CTkFont(size=18, weight="bold"), text_color=COR_AZUL_TEC)
        lbl.pack(pady=20)

        # Container Principal dos Widgets
        self.frame_cards_dash = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        self.frame_cards_dash.pack(fill="x", padx=20, pady=10)
        
        # Grid para 2 colunas de Cards analíticos
        self.frame_cards_dash.columnconfigure(0, weight=1)
        self.frame_cards_dash.columnconfigure(1, weight=1)

        # Inicializa variáveis dos Labels dinâmicos para atualização via estado
        self.lbl_total_livros = self.criar_card_dash("Total de Livros Lidos", "0", 0, 0)
        self.lbl_aproveitamento = self.criar_card_dash("Aproveitamento (Gostou)", "0%", 0, 1)
        self.lbl_top_categoria = self.criar_card_dash("Categoria Mais Lida", "-", 1, 0)
        self.lbl_top_autor = self.criar_card_dash("Autor Favorito", "-", 1, 1)

        # Botão manual para forçar recarregamento das métricas
        btn_refresh = ctk.CTkButton(self.tab_dashboard, text="🔄 Atualizar Indicadores", width=180, fg_color=COR_AZUL_TEC[1], hover_color=COR_AZUL_TEC[0], command=self.atualizar_dashboard)
        btn_refresh.pack(pady=40)

    def criar_card_dash(self, titulo, valor_inicial, linha, coluna):
        """Helper para encapsular o design dos mini-painéis do Dashboard."""
        card = ctk.CTkFrame(self.frame_cards_dash, border_width=1, border_color=("#dbdbdb", "#2d3337"), fg_color=("#ffffff", "#202528"), corner_radius=12)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew")
        
        lbl_tit = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12, weight="normal"), text_color=("#707070", "#a0a0a0"))
        lbl_tit.pack(pady=(12, 2), padx=10)
        
        lbl_val = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=22, weight="bold"), text_color=COR_AZUL_TEC)
        lbl_val.pack(pady=(2, 12), padx=10)
        
        return lbl_val

    def atualizar_dashboard(self):
        """Roda subconsultas agrupadas de Business Intelligence no banco SQLite."""
        # 1. Total de Livros
        self.cursor.execute("SELECT COUNT(*) FROM livros")
        total = self.cursor.fetchone()[0]
        self.lbl_total_livros.configure(text=str(total))

        if total > 0:
            # 2. Taxa de Aproveitamento (Proporção de respostas 'Sim')
            self.cursor.execute("SELECT COUNT(*) FROM livros WHERE avaliacao = 'Sim'")
            sim = self.cursor.fetchone()[0]
            pct = int((sim / total) * 100)
            self.lbl_aproveitamento.configure(text=f"{pct}%", text_color=COR_VERDE_INT[0] if pct >= 70 else COR_AZUL_TEC[0])

            # 3. Categoria predominante
            self.cursor.execute("SELECT categoria, COUNT(categoria) as qt FROM livros WHERE categoria != '' GROUP BY categoria ORDER BY qt DESC LIMIT 1")
            res_cat = self.cursor.fetchone()
            self.lbl_top_categoria.configure(text=str(res_cat[0]) if res_cat else "Nenhuma")

            # 4. Autor mais lido
            self.cursor.execute("SELECT autor, COUNT(autor) as qt FROM livros WHERE autor != '' GROUP BY autor ORDER BY qt DESC LIMIT 1")
            res_aut = self.cursor.fetchone()
            self.lbl_top_autor.configure(text=str(res_aut[0]) if res_aut else "Nenhum")
        else:
            self.lbl_aproveitamento.configure(text="0%")
            self.lbl_top_categoria.configure(text="-")
            self.lbl_top_autor.configure(text="-")

    # =========================================================================
    # MOTOR DE IMPRESSÃO: GERAÇÃO E OPERAÇÃO DE PDF
    # =========================================================================
    def gerar_pdf_resumo(self, titulo, autor, categoria, resumo):
        """Gera um PDF estruturado na pasta temp do sistema e o abre em tela para impressão."""
        # Define caminho temporário seguro multiplataforma
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        # Montagem estruturada do documento ReportLab
        doc = SimpleDocTemplate(temp_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()

        # Customização tipográfica alinhada com as cores e estrutura corporativa
        title_style = ParagraphStyle(
            'PDFTitle', parent=styles['Heading1'], fontSize=22, leading=26, textColor='#0066FF', spaceAfter=6
        )
        meta_style = ParagraphStyle(
            'PDFMeta', parent=styles['Normal'], fontSize=11, leading=14, textColor='#333333', spaceAfter=15
        )
        body_style = ParagraphStyle(
            'PDFBody', parent=styles['Normal'], fontSize=12, leading=20, textColor='#202528', alignment=4 # Justificado
        )

        # Elementos do fluxo de impressão
        story.append(Paragraph(f"Ficha de Leitura: {titulo}", title_style))
        story.append(Paragraph(f"<b>Autor:</b> {autor or 'Não informado'}   |   <b>Categoria:</b> {categoria or 'Geral'}", meta_style))
        story.append(Spacer(1, 10))
        
        # Tratamento de quebras de linha vindas da caixa de texto
        resumo_formatado = resumo.replace('\n', '<br/>') if resumo else "Nenhum resumo registrado para esta obra."
        story.append(Paragraph(f"<b>Resumo da Obra:</b><br/><br/>{resumo_formatado}", body_style))

        # Compila e gera o arquivo físico
        doc.build(story)

        # Executa o dispatch nativo do arquivo de acordo com o Sistema Operacional detectado
        try:
            if os.name == 'nt':  # Windows
                os.startfile(temp_path)
            elif os.platform == 'darwin':  # macOS
                subprocess.run(['open', temp_path])
            else:  # Linux e derivados
                subprocess.run(['xdg-open', temp_path])
        except Exception as e:
            print(f"Erro ao disparar visualização do PDF: {e}")

if __name__ == "__main__":
    app = AppLeituraCompleto()
    app.mainloop()