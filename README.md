# 🖥️ VM Translator — Tradutor VM para Assembly Hack

Tradutor de código intermediário VM para Assembly Hack, desenvolvido em Python.

---

## 👥 Integrantes

- Davi Oliveira Cortes
- Fernando da Silva Costa 

---

## 📁 Estrutura do Projeto

vmtranslator/
├── vm_translator/
│   ├── parser.py           # Analisador de arquivos .vm
│   ├── code_writer.py      # Gerador de código Assembly Hack
│   └── main.py             # Orquestrador
│
├── tests/
│   ├── vm_files/           # Arquivos .vm para testes
│   │   ├── BasicTest.vm
│   │   ├── PointerTest.vm
│   │   ├── SimpleAdd.vm
│   │   ├── StackTest.vm
│   │   └── StaticTest.vm
│   ├── test_parser.py
│   ├── test_code_writer.py
│   └── test_integration.py
│
├── .gitignore
└── README.md

---

## 🧠 Como Funciona

### Pipeline de Tradução

Código VM → Parser → CodeWriter → Assembly Hack

### Etapa 1 — Parser

Lê o arquivo .vm, remove comentários e tokeniza os comandos.

Exemplo:

push constant 10  →  ['push', 'constant', '10']
add               →  ['add']
pop local 0       →  ['pop', 'local', '0']

### Tipos de Comandos Suportados

| Tipo | Exemplos |
|------|----------|
| C_ARITHMETIC | add, sub, neg, eq, gt, lt, and, or, not |
| C_PUSH | push constant 10, push local 0 |
| C_POP | pop local 0, pop argument 1 |
| C_LABEL | label LOOP |
| C_GOTO | goto LOOP |
| C_IF | if-goto LOOP |
| C_FUNCTION | function Main.main 2 |
| C_CALL | call Main.soma 2 |
| C_RETURN | return |

### Etapa 2 — CodeWriter

Traduz cada comando VM para instruções Assembly Hack válidas para a CPU Hack.

Exemplo de tradução:

push constant 10  →  @10
                     D=A
                     @SP
                     A=M
                     M=D
                     @SP
                     M=M+1

### Segmentos de Memória Suportados

| Segmento | Descrição | Endereço Base |
|----------|-----------|---------------|
| constant | Valores imutáveis | N/A |
| local | Variáveis locais | LCL (RAM[1]) |
| argument | Argumentos da função | ARG (RAM[2]) |
| this | Base para objetos | THIS (RAM[3]) |
| that | Base para estruturas dinâmicas | THAT (RAM[4]) |
| temp | Registradores temporários | RAM[5]–RAM[12] |
| pointer | Acesso a this/that | RAM[3] ou RAM[4] |
| static | Variáveis estáticas | StaticBase + index |

---

### Parte 2 — Controle de Fluxo e Sub-rotinas

Controle de fluxo:

| Comando VM | Assembly gerado |
|------------|----------------|
| label LOOP | (funcao$LOOP) |
| goto LOOP | @funcao$LOOP / 0;JMP |
| if-goto LOOP | @SP / AM=M-1 / D=M / @funcao$LOOP / D;JNE |

Sub-rotinas:

- write_function → gera rótulo e inicializa variáveis locais com 0
- write_call → salva frame do chamador e salta para a função
- write_return → restaura frame e retorna para o chamador
- write_init → bootstrap: SP=256 e call Sys.init

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.12+
- pytest

### Instalando o pytest

pip install pytest

### Traduzindo um arquivo .vm

python vmtranslator/main.py caminho/arquivo.vm

### Exemplo de uso

python vmtranslator/main.py tests/vm_files/SimpleAdd.vm

Isso irá gerar o arquivo SimpleAdd.asm no mesmo diretório.

### Rodando os Testes

python -m pytest tests/ -v -s

---

## 🧪 Testes

O projeto segue a metodologia TDD (Test Driven Development).

### Parser
- ✅ has_more_commands, advance e command_type
- ✅ arg1 e arg2 para todos os tipos de comando
- ✅ Ignorar comentários de linha e inline
- ✅ Múltiplos comandos sequenciais
- ✅ label, goto, if-goto, function, call e return

### CodeWriter
- ✅ push e pop para todos os segmentos
- ✅ Operações aritméticas: add, sub, neg
- ✅ Operações lógicas: and, or, not
- ✅ Operações relacionais: eq, gt, lt com labels únicos
- ✅ Controle de fluxo: label, goto, if-goto
- ✅ Sub-rotinas: function, call, return
- ✅ Bootstrap: write_init

### Integração
- ✅ SimpleAdd.vm
- ✅ BasicTest.vm
- ✅ PointerTest.vm
- ✅ StackTest.vm
- ✅ StaticTest.vm


---

## 📦 Arquivos Principais

### parser.py
Lê o arquivo .vm, remove comentários de linha e inline, e tokeniza os comandos. Classifica cada comando em um dos 9 tipos suportados.

### code_writer.py
Gera o código Assembly Hack para cada comando VM. Usa labels únicos para operações relacionais e de controle de fluxo, R13 como registrador auxiliar para pop em segmentos indexados, R14 para endFrame e R15 para retAddress no comando return.

### main.py
Ponto de entrada do tradutor. Aceita um arquivo .vm ou uma pasta como argumento. No modo pasta, gera um único .asm com bootstrap automático no início.

---

