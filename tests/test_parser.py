import os
import tempfile
from parser import Parser, CommandType


def create_temp_vm(content: str) -> str:
    """Cria um arquivo .vm temporário para testes."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.vm', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_has_more_commands():
    """Testa se há mais comandos para processar."""
    path = create_temp_vm("push constant 10\n")
    parser = Parser(path)
    assert parser.has_more_commands() == True
    os.unlink(path)
    print("✅ Teste de has_more_commands passou!")


def test_advance():
    """Testa o avanço para o próximo comando."""
    path = create_temp_vm("push constant 10\n")
    parser = Parser(path)
    parser.advance()
    assert parser.current == ['push', 'constant', '10']
    os.unlink(path)
    print("✅ Teste de advance passou!")


def test_command_type_push():
    """Testa o tipo de comando push."""
    path = create_temp_vm("push constant 10\n")
    parser = Parser(path)
    parser.advance()
    assert parser.command_type() == CommandType.C_PUSH
    os.unlink(path)
    print("✅ Teste de command_type push passou!")


def test_command_type_pop():
    """Testa o tipo de comando pop."""
    path = create_temp_vm("pop local 0\n")
    parser = Parser(path)
    parser.advance()
    assert parser.command_type() == CommandType.C_POP
    os.unlink(path)
    print("✅ Teste de command_type pop passou!")


def test_command_type_arithmetic():
    """Testa o tipo de comando aritmético."""
    for cmd in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
        path = create_temp_vm(f"{cmd}\n")
        parser = Parser(path)
        parser.advance()
        assert parser.command_type() == CommandType.C_ARITHMETIC
        os.unlink(path)
    print("✅ Teste de command_type arithmetic passou!")


def test_arg1_push():
    """Testa o primeiro argumento de um push."""
    path = create_temp_vm("push constant 10\n")
    parser = Parser(path)
    parser.advance()
    assert parser.arg1() == 'constant'
    os.unlink(path)
    print("✅ Teste de arg1 push passou!")


def test_arg1_arithmetic():
    """Testa o primeiro argumento de um comando aritmético."""
    path = create_temp_vm("add\n")
    parser = Parser(path)
    parser.advance()
    assert parser.arg1() == 'add'
    os.unlink(path)
    print("✅ Teste de arg1 arithmetic passou!")


def test_arg2():
    """Testa o segundo argumento de um push."""
    path = create_temp_vm("push constant 42\n")
    parser = Parser(path)
    parser.advance()
    assert parser.arg2() == 42
    os.unlink(path)
    print("✅ Teste de arg2 passou!")


def test_ignore_comments():
    """Testa se comentários são ignorados."""
    path = create_temp_vm(
        "// comentario\n"
        "push constant 10 // comentario inline\n"
    )
    parser = Parser(path)
    parser.advance()
    assert parser.current == ['push', 'constant', '10']
    os.unlink(path)
    print("✅ Teste de ignorar comentários passou!")


def test_multiple_commands():
    """Testa múltiplos comandos."""
    path = create_temp_vm(
        "push constant 10\n"
        "push constant 20\n"
        "add\n"
    )
    parser = Parser(path)

    parser.advance()
    assert parser.command_type() == CommandType.C_PUSH

    parser.advance()
    assert parser.command_type() == CommandType.C_PUSH

    parser.advance()
    assert parser.command_type() == CommandType.C_ARITHMETIC

    assert parser.has_more_commands() == False
    os.unlink(path)
    print("✅ Teste de múltiplos comandos passou!")

