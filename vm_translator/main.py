import sys
import os
from vm_translator.parser import Parser, CommandType
from vm_translator.code_writer import CodeWriter


def translate(parser: Parser, cw: CodeWriter):
    """Traduz todos os comandos de um parser para o code writer."""
    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()

        if cmd_type == CommandType.C_ARITHMETIC:
            cw.write_arithmetic(parser.arg1())
        elif cmd_type == CommandType.C_PUSH:
            cw.write_push(parser.arg1(), parser.arg2())
        elif cmd_type == CommandType.C_POP:
            cw.write_pop(parser.arg1(), parser.arg2())
        elif cmd_type == CommandType.C_LABEL:        
            cw.write_label(parser.arg1())
        elif cmd_type == CommandType.C_GOTO:        
            cw.write_goto(parser.arg1())
        elif cmd_type == CommandType.C_IF:          
            cw.write_if(parser.arg1())
        elif cmd_type == CommandType.C_FUNCTION:     
            cw.write_function(parser.arg1(), parser.arg2())
        elif cmd_type == CommandType.C_CALL:         
            cw.write_call(parser.arg1(), parser.arg2())
        elif cmd_type == CommandType.C_RETURN:       
            cw.write_return()


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <arquivo.vm ou pasta>")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"Caminho não encontrado: {path}")
        sys.exit(1)

    # compila uma pasta inteira
    if os.path.isdir(path):
        vm_files = [f for f in os.listdir(path) if f.endswith('.vm')]
        output_path = os.path.join(path, os.path.basename(path) + '.asm')

        cw = CodeWriter(output_path)
        cw.write_init()  # bootstrap

        for vm_file in vm_files:
            vm_path = os.path.join(path, vm_file)
            cw.set_filename(vm_file.replace('.vm', ''))
            print(f"Traduzindo {vm_path}...")
            parser = Parser(vm_path)
            translate(parser, cw)

        cw.close()
        print(f"Gerado: {output_path}")

    # compila um único arquivo
    elif os.path.isfile(path):
        if not path.endswith('.vm'):
            print("O arquivo deve ter extensão .vm")
            sys.exit(1)

        output_path = path.replace('.vm', '.asm')
        cw = CodeWriter(output_path)
        cw.set_filename(os.path.basename(path).replace('.vm', ''))
        parser = Parser(path)
        translate(parser, cw)
        cw.close()
        print(f"✅ Gerado: {output_path}")


if __name__ == '__main__':
    main()

