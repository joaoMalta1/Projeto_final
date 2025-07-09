# Projeto de Sistema de Contagem Inteligente

Este projeto oferece uma solução completa para gerenciamento e visualização de dados de contagem, integrando um dispositivo Arduino físico, uma interface web para configuração e um aplicativo de desktop para análise de dados e geração de relatórios.

## Visão Geral do Projeto

O sistema permite que os usuários:
* Definam diferentes "conjuntos de contagem", cada um com múltiplos contadores.
* Enviem configurações personalizadas para um dispositivo Arduino.
* Recebam dados de contagem atualizados do Arduino, incluindo um histórico de eventos.
* Visualizem os dados em tempo real através de gráficos interativos.
* Exportem e compartilhem relatórios em diversos formatos (Excel, Google Sheets, PDF, E-mail, Telegram).

## Componentes do Projeto

O projeto é dividido em três componentes principais:

1.  **Código Arduino (`.ino`)**: O firmware para o dispositivo físico de contagem, responsável pela interação com botões, exibição em tela, persistência de dados na EEPROM e comunicação serial.
2.  **Interface Web (Python/Flask)**: Uma aplicação web para gerenciar os conjuntos de contagem, adicionar novos contadores e orquestrar a comunicação com o Arduino.
3.  **Aplicativo Desktop (Python/Tkinter)**: Uma ferramenta para visualização de dados em gráficos dinâmicos, com funcionalidades de exportação e integração com serviços de nuvem e comunicação.

---

### 1. Código Arduino

O código Arduino (`.ino`) é o software embarcado no microcontrolador que gerencia a lógica do dispositivo de contagem.

**Funcionalidades Principais:**

* **Interação com Botões**: Controla quatro botões físicos. Um toque rápido incrementa a contagem, enquanto um toque longo (acima de 1 segundo) decrementa.
* **Exibição em Tela LCD TFT**: Utiliza a biblioteca `MCUFRIEND_kbv` para exibir o título do conjunto de contagem, os nomes dos contadores e suas respectivas quantidades. Cada contador é exibido em uma cor diferente para facilitar a identificação.
* **Persistência de Dados (EEPROM)**: Armazena o título do conjunto, o número de contadores, os detalhes de cada contador (nome, unidade, passo, quantidade atual) e o histórico de eventos de botões pressionados na memória EEPROM. Isso garante que os dados não sejam perdidos mesmo quando o dispositivo é desligado. Os dados são salvos na EEPROM após 5 segundos de inatividade para prolongar a vida útil da memória.
* **Monitoramento de Bateria**: Lê o nível da bateria e exibe a porcentagem restante na tela. O sistema utiliza um divisor de tensão e um pino de controle para otimizar a leitura da bateria.
* **Comunicação Serial Bidirecional**:
    * **Recebe Configurações**: Aguarda comandos da interface web via serial para configurar os contadores (título, nomes, passos, unidades, quantidades iniciais).
    * **Envia Dados**: Ao receber um comando "enviar", formata e envia os dados atuais dos contadores e todo o histórico de eventos de botões para a interface web. O histórico é resetado na EEPROM após o envio para evitar duplicação.


**Estrutura de Dados:**

* `struct contagem`: Define cada contador com `nome`, `unidade`, `passo` (valor de incremento/decremento) e `qtd` (quantidade atual).
* `botao_press[]`: Armazena o histórico de cada ação de botão (incremento/decremento para cada contador).

**Prototipo simulado:**

![micro_fritz](https://github.com/user-attachments/assets/a7eccf16-9b0b-4d59-ac9f-b325dde11707)

---

### 2. Interface Web (Python/Flask)

A aplicação web é construída com Flask e atua como a ponte entre o usuário e o dispositivo Arduino, além de gerenciar o banco de dados de conjuntos de contagem.

**Funcionalidades Principais:**

* **Gerenciamento de Conjuntos**:
    * Página inicial (`/`): Lista todos os conjuntos de contagem existentes, carregados de `db/conjuntos.json`.
    * Registro (`/registra_conjunto`): Permite criar novos conjuntos de contagem, cada um com um título e um histórico vazio inicialmente.
    * Visualização de Contadores (`/conjuntos/<titulo_conjunto>`): Exibe os contadores específicos de um conjunto selecionado.
    * Adição de Contadores (`/adiciona_contagem/<titulo_conjunto>`): Permite adicionar novos contadores a um conjunto existente, definindo nome, passo e unidade.
* **Comunicação com Arduino**:
    * **Envio de Configurações (`/envia_arduino/<titulo_conjunto>`):** Pega os dados de um conjunto selecionado do `db/conjuntos.json`, formata-os em uma string (título, número de contadores, e para cada contador: nome, passo, unidade, quantidade) e os envia via serial para o Arduino. Aguarda uma resposta do Arduino para confirmar o sucesso.
    * **Recebimento de Dados (`/recebe_arduino`):** Envia um comando "enviar" para o Arduino via serial. Recebe a resposta do Arduino, que contém os dados atualizados dos contadores e o histórico de eventos. A função `trata_resposta` analisa essa string e atualiza o arquivo `db/conjuntos.json` com as novas quantidades e o histórico de cada contador.
* **Armazenamento de Dados**: Utiliza um arquivo `db/conjuntos.json` para persistir todas as configurações dos conjuntos de contagem e os dados dos contadores.
* **Tratamento de Erros**: Páginas de erro personalizadas para 404 e 500.

---

### 3. Aplicativo Desktop (Python/Tkinter)

Este aplicativo de desktop oferece ferramentas avançadas de visualização de dados e relatórios, funcionando de forma autônoma e em sincronia com as atualizações do banco de dados.

**Funcionalidades Principais:**

* **Visualização Gráfica Dinâmica**:
    * **Seleção de Conjunto e Tipo de Gráfico**: Permite escolher o conjunto de contagem e o tipo de gráfico (linha, barra, pizza) através de comboboxes.
    * **Gráfico de Linha**: Mostra a evolução das contagens ao longo do tempo, utilizando o histórico de eventos.
    * **Gráfico de Barra**: Exibe o total atual de cada contador em um gráfico de barras.
    * **Gráfico de Pizza**: Apresenta a distribuição percentual das contagens atuais.
* **Monitoramento em Tempo Real**: Uma thread em segundo plano monitora o arquivo `db/conjuntos.json`. Qualquer alteração no arquivo (e.g., após o recebimento de dados do Arduino pela interface web) dispara a atualização automática dos gráficos e dos dados no aplicativo.
* **Exportação e Integração de Dados**:
    * **Exportação para Excel (`cria_excel`)**: Gera ou atualiza arquivos `.xlsx` com os dados de contagem para cada conjunto.
    * **Atualização do Google Sheets (`atualizar_google_sheets`)**: Sincroniza os dados de contagem com planilhas no Google Sheets, utilizando credenciais de serviço para autenticação.
    * **Geração de Relatórios em PDF (`gerar_relatorio_pdf`)**: Cria relatórios detalhados em formato PDF com os dados de contagem.
    * **Envio por E-mail (`enviar_email_com_pdf`)**: Permite enviar os relatórios em PDF para um endereço de e-mail especificado. O último e-mail utilizado é salvo para conveniência.
    * **Integração com Telegram (`enviar_mensagem_telegram`)**: Envia mensagens formatadas com os dados de contagem para um chat específico do Telegram.

## Como Iniciar o Projeto

### Pré-requisitos

* **Arduino IDE**: Para programar o dispositivo Arduino.
* **Python 3.x**: Para as aplicações web e desktop.
* **Bibliotecas Python**: `Flask`, `matplotlib`, `tkinter`, `pandas`, `gspread`, `oauth2client`, `fpdf`, `requests`, `smtplib`.
* **Bibliotecas Arduino**: `Adafruit_GFX`, `MCUFRIEND_kbv`, `GFButton`, `EEPROM`.
* **Credenciais Google Sheets**: Um arquivo JSON de credenciais de conta de serviço para a integração com o Google Sheets.
* **Token de Bot Telegram**: Para a integração com o Telegram.
* **Senha de Aplicativo Gmail**: Para o envio de e-mails (não a senha da sua conta principal).

### Instalação e Configuração

1.  **Configurar Arduino**:
    * Abra o código Arduino (`.ino`) na IDE do Arduino.
    * Instale as bibliotecas necessárias via Gerenciador de Bibliotecas da IDE (Adafruit GFX Library, MCUFRIEND_kbv, GFButton).
    * Conecte os botões, a tela LCD TFT e o circuito de monitoramento da bateria conforme o hardware do seu projeto.
    * Faça o upload do código para o seu Arduino.
2.  **Configurar Ambiente Python**:
    * Crie um ambiente virtual (recomendado): `python -m venv venv`
    * Ative o ambiente:
        * Windows: `venv\Scripts\activate`
        * macOS/Linux: `source venv/bin/activate`
    * Instale as dependências: `pip install Flask matplotlib pandas gspread oauth2client fpdf requests` (Note: `tkinter` e `smtplib` são geralmente parte da instalação padrão do Python).
3.  **Configurar Credenciais (Google Sheets e Telegram)**:
    * Crie um arquivo `Credentials.json` na raiz do projeto para o Google Sheets.
    * Configure o token do seu bot Telegram e o `chat_id` dentro do arquivo `graficos_integracao_planilhas.py`.
    * Configure o e-mail do remetente e a senha de aplicativo do Gmail em `graficos_integracao_planilhas.py`.
4.  **Estrutura de Pastas**:
    * Crie uma pasta `db` na raiz do projeto.
    * Dentro de `db`, o arquivo `conjuntos.json` será criado e gerenciado automaticamente.
    * Crie uma pasta `html` para os templates Flask (`home.html`, `conjuntos.html`, `erro.html`).

### Execução

1.  **Iniciar Interface Web**:
    * No terminal, na raiz do projeto, execute: `python interface.py`
    * Acesse a interface no seu navegador (geralmente `http://127.0.0.1:5000/`).
2.  **Iniciar Aplicativo Desktop**:
    * Em um terminal **separado**, na raiz do projeto, execute: `python graficos_integracao_planilhas.py`
    * A janela do aplicativo desktop será aberta, exibindo os gráficos.

## Fluxo de Uso

1.  **Interface Web**: Crie e gerencie seus conjuntos de contagem.
2.  **Enviar para Arduino**: Use a interface web para enviar a configuração de um conjunto para o Arduino.
3.  **Interagir com Arduino**: Use os botões físicos do dispositivo Arduino para realizar as contagens. Os dados serão salvos na EEPROM.
4.  **Receber do Arduino**: Use a interface web para buscar os dados atualizados do Arduino. Isso atualizará o `db/conjuntos.json`.
5.  **Visualizar no Desktop**: O aplicativo desktop detectará automaticamente a mudança no `db/conjuntos.json`, atualizará os gráficos e gerará os relatórios (Excel, Google Sheets, PDF) em segundo plano.
6.  **Compartilhar**: No aplicativo desktop, você pode enviar o relatório PDF por e-mail ou enviar os dados atuais para o Telegram.
