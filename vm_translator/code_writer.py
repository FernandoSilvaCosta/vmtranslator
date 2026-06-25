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


    def write_function(self, function_name: str, n_locals: int):
        """Gera código Assembly para o comando function."""
        self._write(f'// function {function_name} {n_locals}')
        self._current_function = function_name  # 🆕 atualiza a função atual
        self._write(f'({function_name})')

        # inicializa as variáveis locais com 0
        for _ in range(n_locals):
            self._write(
                '@SP',
                'A=M',
                'M=0',
                '@SP',
                'M=M+1',
            )

    def write_call(self, function_name: str, n_args: int):
        """Gera código Assembly para o comando call."""
        return_label = f'{function_name}$ret{self._return_count}'
        self._return_count += 1

        self._write(f'// call {function_name} {n_args}')

        # push return address
        self._write(f'@{return_label}', 'D=A')
        self._push_d()

        # push LCL
        self._write('@LCL', 'D=M')
        self._push_d()

        # push ARG
        self._write('@ARG', 'D=M')
        self._push_d()

        # push THIS
        self._write('@THIS', 'D=M')
        self._push_d()

        # push THAT
        self._write('@THAT', 'D=M')
        self._push_d()

        # ARG = SP - 5 - nArgs
        self._write(
            '@SP',
            'D=M',
            f'@{5 + n_args}',
            'D=D-A',
            '@ARG',
            'M=D',
        )

        # LCL = SP
        self._write(
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
        )

        # goto functionName
        self._write(f'@{function_name}', '0;JMP')

        # return label
        self._write(f'({return_label})')

    def write_return(self):
        """Gera código Assembly para o comando return."""
        self._write('// return')

        # endFrame = LCL → guarda em R14
        self._write(
            '@LCL',
            'D=M',
            '@R14',
            'M=D',
        )

        # retAddress = *(endFrame-5) → guarda em R15
        self._write(
            '@5',
            'A=D-A',
            'D=M',
            '@R15',
            'M=D',
        )

        # *ARG = pop()
        self._pop_d()
        self._write(
            '@ARG',
            'A=M',
            'M=D',
        )

        # SP = ARG + 1
        self._write(
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',
        )

        # THAT = *(endFrame-1)
        self._write(
            '@R14',
            'AM=M-1',
            'D=M',
            '@THAT',
            'M=D',
        )

        # THIS = *(endFrame-2)
        self._write(
            '@R14',
            'AM=M-1',
            'D=M',
            '@THIS',
            'M=D',
        )

        # ARG = *(endFrame-3)
        self._write(
            '@R14',
            'AM=M-1',
            'D=M',
            '@ARG',
            'M=D',
        )

        # LCL = *(endFrame-4)
        self._write(
            '@R14',
            'AM=M-1',
            'D=M',
            '@LCL',
            'M=D',
        )

        # goto retAddress
        self._write(
            '@R15',
            'A=M',
            '0;JMP',
        )

    def write_init(self):
        """Gera código de bootstrap: SP=256 e call Sys.init."""
        self._write('// bootstrap')
        self._write(
            '@256',
            'D=A',
            '@SP',
            'M=D',
        )
        self.write_call('Sys.init', 0)

