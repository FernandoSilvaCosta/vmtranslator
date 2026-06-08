
import sys
import os

from vm_translator.parser import Parser, CommandType
from vm_translator.code_writer import CodeWriter


def translate(input_file: str):
    output_file = input_file.replace('.vm', '.asm')

    p = Parser(input_file)
    cw = CodeWriter(output_file)

    while p.has_more_commands():
        p.advance()
        cmd_type = p.command_type()

        if cmd_type == CommandType.C_ARITHMETIC:
            cw.write_arithmetic(p.arg1())
        elif cmd_type == CommandType.C_PUSH:
            cw.write_push(p.arg1(), p.arg2())
        elif cmd_type == CommandType.C_POP:
            cw.write_pop(p.arg1(), p.arg2())

    cw.close()
    print(f"Tradução concluída: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.vm>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Erro: arquivo '{input_file}' não encontrado.")
        sys.exit(1)

    if not input_file.endswith('.vm'):
        print("Erro: o arquivo deve ter extensão .vm")
        sys.exit(1)

    translate(input_file)


if __name__ == '__main__':
    main()
