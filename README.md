# AppLeitura - Biblios
App para controlar os arquivos lidos no período

# 📖 Gerenciador de Leituras Anuais

Um aplicativo desktop moderno desenvolvido em **Python** para controle, análise e registro de leituras. O sistema permite catalogar livros lidos, escrever resumos detalhados, visualizar indicadores de desempenho e exportar fichas de leitura diretamente para **PDF/Impressão**.

---

## 🎨 Identidade Visual & Design
O aplicativo foi projetado seguindo diretrizes modernas de UI/UX, utilizando cantos arredondados, responsividade a temas nativos (Dark/Light mode) e uma paleta de cores institucional baseada em tecnologia e eficiência:
*   **Azul Tecnologia (`#0078D4`):** Utilizado em botões de ação e componentes em foco.
*   **Verde Inteligência (`#107C41` / `#00FFAD`):** Destaque para taxas de aproveitamento positivo e aprovações.
*   **Cinza Grafite (`#202528`):** Aplicado nos fundos de cartões e tipografia principal para evitar cansaço visual.
*   **Branco Gelo (`#F8F9FA`):** Fundo principal no modo claro.

---

## 🚀 Funcionalidades

1.  **📝 Cadastro de Leituras:**
    *   Registro de Título, Autor, Categoria e Ano de Publicação.
    *   Menu de avaliação intuitivo (*Sim, Não, Mais ou menos*).
    *   Área de texto dedicada para resumos de até 20 linhas.
2.  **🔍 Consulta Avançada:**
    *   Filtros dinâmicos em tempo real por **Ano**, **Categoria** ou **Autor**.
    *   Pesquisa parcial utilizando o operador `LIKE` no banco de dados.
    *   Visualização baseada em *Cards* modernos com rolagem suave.
3.  **🖨️ Exportação e Impressão:**
    *   Botão nativo em cada cartão para gerar a ficha do livro em **PDF** formatado e justificado.
    *   Abertura automática no leitor padrão do sistema operacional para envio direto à impressora.
4.  **📊 Dashboard Analítico:**
    *   Contador total de livros lidos no ano.
    *   Métrica de **Aproveitamento %** baseado nas avaliações positivas.
    *   Cálculo automático da **Categoria mais lida** e do **Autor favorito**.

---

## 🛠️ Tecnologias Utilizadas

*   **Python 3.10+** (Compatível com versões recentes como Python 3.14).
*   **CustomTkinter:** Biblioteca para interface gráfica moderna com suporte a temas do sistema.
*   **SQLite3:** Banco de dados relacional leve e embutido (sem necessidade de servidores externos).
*   **ReportLab:** Engine robusta para geração de documentos PDF sob demanda.

---

## 📦 Como Instalar e Executar

### 1. Pré-requisitos
Certifique-se de ter o Python instalado na sua máquina. Em seguida, clone este repositório ou baixe o arquivo do código.

### 2. Instalação das Dependências
Instale as bibliotecas necessárias através do terminal/prompt de comando:

```bash
pip install customtkinter reportlab

### 3. Executando o AplicativoNavegue até a pasta do projeto e execute o script principal:Bashpython app.py

Nota: O banco de dados biblioteca_pessoal.db será criado automaticamente no mesmo diretório na primeira execução.📂 Estrutura do Banco de DadosO banco de dados local possui a seguinte modelagem na tabela livros:CampoTipoDescriçãoidINTEGERChave primária com autoincrementotituloTEXTNome da obra (Obrigatório)autorTEXTNome do autorcategoriaTEXTGênero ou área do conhecimentoano_publicacaoTEXTAno de lançamento ou leituraavaliacaoTEXTFeedback (Sim, Não, Mais ou menos)resumoTEXTTexto com a síntese da obra📝 LicençaEste projeto é de uso livre para fins de estudo, organização pessoal e desenvolvimento contínuo.

### 💡 Dica:
Basta copiar esse bloco de código, colá-lo em um arquivo de texto comum e salvá-lo com o nome *
