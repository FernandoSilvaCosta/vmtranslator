import os
import tempfile
from vm_translator.code_writer import CodeWriter


def create_temp_asm() -> tuple:
    """Cria um arquivo .asm temporário para testes."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False)
    tmp.close()
    return tmp.name


def read_asm(path: str) -> str:
    """Lê o conteúdo do arquivo .asm gerado."""
    with open(path, 'r') as f:
        return f.read()


def test_push_constant():
    """Testa a geração de código para push constant."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_push('constant', 10)
    cw.close()

    asm = read_asm(path)
    assert '@10' in asm
    assert 'D=A' in asm
    assert '@SP' in asm
    assert 'M=M+1' in asm
    os.unlink(path)
    print("✅ Teste de push constant passou!")


def test_push_local():
    """Testa a geração de código para push local."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_push('local', 0)
    cw.close()

    asm = read_asm(path)
    assert '@LCL' in asm
    assert 'D=M' in asm
    os.unlink(path)
    print("✅ Teste de push local passou!")


def test_pop_local():
    """Testa a geração de código para pop local."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_pop('local', 0)
    cw.close()

    asm = read_asm(path)
    assert '@LCL' in asm
    assert '@R13' in asm
    assert 'M=D' in asm
    os.unlink(path)
    print("✅ Teste de pop local passou!")


def test_push_temp():
    """Testa a geração de código para push temp."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_push('temp', 2)
    cw.close()

    asm = read_asm(path)
    assert '@7' in asm  # 5 + 2
    os.unlink(path)
    print("✅ Teste de push temp passou!")


def test_pop_temp():
    """Testa a geração de código para pop temp."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_pop('temp', 2)
    cw.close()

    asm = read_asm(path)
    assert '@7' in asm  # 5 + 2
    os.unlink(path)
    print("✅ Teste de pop temp passou!")


def test_push_pointer():
    """Testa a geração de código para push pointer."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_push('pointer', 0)
    cw.close()

    asm = read_asm(path)
    assert '@THIS' in asm
    os.unlink(path)
    print("✅ Teste de push pointer passou!")


def test_pop_pointer():
    """Testa a geração de código para pop pointer."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_pop('pointer', 1)
    cw.close()

    asm = read_asm(path)
    assert '@THAT' in asm
    os.unlink(path)
    print("✅ Teste de pop pointer passou!")


def test_arithmetic_add():
    """Testa a geração de código para add."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('add')
    cw.close()

    asm = read_asm(path)
    assert 'M=D+M' in asm
    os.unlink(path)
    print("✅ Teste de add passou!")


def test_arithmetic_sub():
    """Testa a geração de código para sub."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('sub')
    cw.close()

    asm = read_asm(path)
    assert 'M=M-D' in asm
    os.unlink(path)
    print("✅ Teste de sub passou!")


def test_arithmetic_neg():
    """Testa a geração de código para neg."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('neg')
    cw.close()

    asm = read_asm(path)
    assert 'M=-M' in asm
    os.unlink(path)
    print("✅ Teste de neg passou!")


def test_arithmetic_eq():
    """Testa a geração de código para eq."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('eq')
    cw.close()

    asm = read_asm(path)
    assert 'JEQ' in asm
    assert 'M=-1' in asm
    assert 'M=0' in asm
    os.unlink(path)
    print("✅ Teste de eq passou!")


def test_arithmetic_gt():
    """Testa a geração de código para gt."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('gt')
    cw.close()

    asm = read_asm(path)
    assert 'JGT' in asm
    os.unlink(path)
    print("✅ Teste de gt passou!")


def test_arithmetic_lt():
    """Testa a geração de código para lt."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('lt')
    cw.close()

    asm = read_asm(path)
    assert 'JLT' in asm
    os.unlink(path)
    print("✅ Teste de lt passou!")


def test_arithmetic_and():
    """Testa a geração de código para and."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('and')
    cw.close()

    asm = read_asm(path)
    assert 'M=D&M' in asm
    os.unlink(path)
    print("✅ Teste de and passou!")


def test_arithmetic_or():
    """Testa a geração de código para or."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('or')
    cw.close()

    asm = read_asm(path)
    assert 'M=D|M' in asm
    os.unlink(path)
    print("✅ Teste de or passou!")


def test_arithmetic_not():
    """Testa a geração de código para not."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw.write_arithmetic('not')
    cw.close()

    asm = read_asm(path)
    assert 'M=!M' in asm
    os.unlink(path)
    print("✅ Teste de not passou!")

def test_write_label():
    """Testa a geração de código para label."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw._current_function = 'Main.main'
    cw.write_label('LOOP')
    cw.close()

    asm = read_asm(path)
    assert '(Main.main$LOOP)' in asm
    os.unlink(path)
    print("✅ Teste de label passou!")


def test_write_goto():
    """Testa a geração de código para goto."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw._current_function = 'Main.main'
    cw.write_goto('LOOP')
    cw.close()

    asm = read_asm(path)
    assert '@Main.main$LOOP' in asm
    assert '0;JMP' in asm
    os.unlink(path)
    print("✅ Teste de goto passou!")


def test_write_if():
    """Testa a geração de código para if-goto."""
    path = create_temp_asm()
    cw = CodeWriter(path)
    cw._current_function = 'Main.main'
    cw.write_if('LOOP')
    cw.close()

    asm = read_asm(path)
    assert '@Main.main$LOOP' in asm
    assert 'D;JNE' in asm
    os.unlink(path)
    print("✅ Teste de if-goto passou!")


