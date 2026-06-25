class CodeWriter:
    """Gera código Assembly Hack a partir de comandos VM."""

    SEGMENTS = {
        'local':    'LCL',
        'argument': 'ARG',
        'this':     'THIS',
        'that':     'THAT',
    }

    def __init__(self, filename: str):
        self._file = open(filename, 'w')
        self._label_count = 0  # contador para labels únicos (eq, gt, lt)
        self._return_count = 0 
        self._static_base = filename.replace('.asm', '').split('/')[-1]
        self._current_function = ''

    def set_filename(self, filename: str):
        """Atualiza o nome do arquivo atual para variáveis estáticas."""
        self._static_base = filename

    def _write(self, *lines: str):
        """Escreve linhas no arquivo .asm."""
        for line in lines:
            self._file.write(line + '\n')

    def _push_d(self):
        """Empilha o valor de D na pilha."""
        self._write(
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1',
        )

    def _pop_d(self):
        """Desempilha o topo da pilha para D."""
        self._write(
            '@SP',
            'AM=M-1',
            'D=M',
        )

    def write_arithmetic(self, cmd: str):
        """Gera código Assembly para um comando aritmético ou lógico."""
        self._write(f'// {cmd}')

        if cmd == 'add':
            self._pop_d()
            self._write('A=A-1', 'M=D+M')

        elif cmd == 'sub':
            self._pop_d()
            self._write('A=A-1', 'M=M-D')

        elif cmd == 'neg':
            self._write('@SP', 'A=M-1', 'M=-M')

        elif cmd == 'and':
            self._pop_d()
            self._write('A=A-1', 'M=D&M')

        elif cmd == 'or':
            self._pop_d()
            self._write('A=A-1', 'M=D|M')

        elif cmd == 'not':
            self._write('@SP', 'A=M-1', 'M=!M')

        elif cmd in ('eq', 'gt', 'lt'):
            label = f'LABEL_{self._label_count}'
            self._label_count += 1

            jump_map = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}
            jump = jump_map[cmd]

            self._pop_d()
            self._write(
                'A=A-1',
                'D=M-D',
                f'@TRUE_{label}',
                f'D;{jump}',
                '@SP',
                'A=M-1',
                'M=0',
                f'@END_{label}',
                '0;JMP',
                f'(TRUE_{label})',
                '@SP',
                'A=M-1',
                'M=-1',
                f'(END_{label})',
            )

    def write_push(self, segment: str, index: int):
        """Gera código Assembly para um comando push."""
        self._write(f'// push {segment} {index}')

        if segment == 'constant':
            self._write(f'@{index}', 'D=A')

        elif segment in self.SEGMENTS:
            self._write(
                f'@{self.SEGMENTS[segment]}',
                'D=M',
                f'@{index}',
                'A=D+A',
                'D=M',
            )

        elif segment == 'temp':
            self._write(f'@{5 + index}', 'D=M')

        elif segment == 'pointer':
            reg = 'THIS' if index == 0 else 'THAT'
            self._write(f'@{reg}', 'D=M')

        elif segment == 'static':
            self._write(f'@{self._static_base}.{index}', 'D=M')

        self._push_d()

    def write_pop(self, segment: str, index: int):
        """Gera código Assembly para um comando pop."""
        self._write(f'// pop {segment} {index}')

        if segment in self.SEGMENTS:
            self._write(
                f'@{self.SEGMENTS[segment]}',
                'D=M',
                f'@{index}',
                'D=D+A',
                '@R13',
                'M=D',
            )
            self._pop_d()
            self._write('@R13', 'A=M', 'M=D')

        elif segment == 'temp':
            self._pop_d()
            self._write(f'@{5 + index}', 'M=D')

        elif segment == 'pointer':
            reg = 'THIS' if index == 0 else 'THAT'
            self._pop_d()
            self._write(f'@{reg}', 'M=D')

        elif segment == 'static':
            self._pop_d()
            self._write(f'@{self._static_base}.{index}', 'M=D')

    def close(self):
        """Fecha o arquivo .asm."""
        self._file.close()

    def write_label(self, label: str):
        """Gera código Assembly para o comando label."""
        self._write(f'// label {label}')
        self._write(f'({self._current_function}${label})')

    def write_goto(self, label: str):
        """Gera código Assembly para o comando goto."""
        self._write(f'// goto {label}')
        self._write(
            f'@{self._current_function}${label}',
            '0;JMP',
        )

    def write_if(self, label: str):
        """Gera código Assembly para o comando if-goto."""
        self._write(f'// if-goto {label}')
        self._write(
            '@SP',
            'AM=M-1',
            'D=M',
            f'@{self._current_function}${label}',
            'D;JNE',
        )


