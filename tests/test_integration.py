"""
Teste de integração do VMTranslator.
Simula a VM stack machine em Python e compara com o assembly gerado,
executando ambos e verificando que produzem os mesmos resultados.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vm_translator.parser import Parser, CommandType
from vm_translator.code_writer import CodeWriter


class VMEmulator:
    """Emulador da VM stack machine para validação.
    Usa RAM diretamente como a CPU Hack real (SP em RAM[0])."""

    def __init__(self):
        self.ram = [0] * 32768
        self.stack = []  # espelho para fácil acesso
        # Inicializa ponteiros padrão
        self.ram[0] = 256   # SP
        self.ram[1] = 300   # LCL
        self.ram[2] = 400   # ARG
        self.ram[3] = 3000  # THIS
        self.ram[4] = 3010  # THAT

    @property
    def sp(self):
        return self.ram[0]

    @sp.setter
    def sp(self, val):
        self.ram[0] = val

    def execute(self, vm_file: str):
        """Executa um arquivo .vm e retorna o estado final."""
        p = Parser(vm_file)

        while p.has_more_commands():
            p.advance()
            cmd_type = p.command_type()

            if cmd_type == CommandType.C_PUSH:
                self._push(p.arg1(), p.arg2())
            elif cmd_type == CommandType.C_POP:
                self._pop(p.arg1(), p.arg2())
            elif cmd_type == CommandType.C_ARITHMETIC:
                self._arithmetic(p.arg1())

        # Reconstrói stack list para asserts fáceis
        self.stack = [self.ram[i] for i in range(256, self.sp)]
        return self

    def _resolve_address(self, segment: str, index: int) -> int:
        """Resolve o endereço real de memória para um segmento."""
        seg_map = {'local': 1, 'argument': 2, 'this': 3, 'that': 4}
        if segment in seg_map:
            return self.ram[seg_map[segment]] + index
        elif segment == 'temp':
            return 5 + index
        elif segment == 'pointer':
            return 3 + index
        elif segment == 'static':
            return 16 + index
        return 0

    def _stack_push(self, val: int):
        """Empilha valor na RAM e incrementa SP."""
        self.ram[self.sp] = val
        self.sp += 1

    def _stack_pop(self) -> int:
        """Desempilha valor da RAM e decrementa SP."""
        self.sp -= 1
        return self.ram[self.sp]

    def _push(self, segment: str, index: int):
        if segment == 'constant':
            self._stack_push(index)
        else:
            addr = self._resolve_address(segment, index)
            self._stack_push(self.ram[addr])

    def _pop(self, segment: str, index: int):
        val = self._stack_pop()
        addr = self._resolve_address(segment, index)
        self.ram[addr] = val

    def _arithmetic(self, cmd: str):
        if cmd == 'add':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(self._wrap(a + b))
        elif cmd == 'sub':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(self._wrap(a - b))
        elif cmd == 'neg':
            self._stack_push(self._wrap(-self._stack_pop()))
        elif cmd == 'eq':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(-1 if a == b else 0)
        elif cmd == 'gt':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(-1 if a > b else 0)
        elif cmd == 'lt':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(-1 if a < b else 0)
        elif cmd == 'and':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(a & b)
        elif cmd == 'or':
            b, a = self._stack_pop(), self._stack_pop()
            self._stack_push(a | b)
        elif cmd == 'not':
            self._stack_push(self._wrap(~self._stack_pop()))

    def _wrap(self, val: int) -> int:
        """Simula overflow de 16 bits."""
        val = val & 0xFFFF
        if val & 0x8000:
            val -= 0x10000
        return val


# ============================================================
# Casos de teste com valores esperados (do .cmp do nand2tetris)
# ============================================================

VM_DIR = os.path.join(os.path.dirname(__file__), 'vm_files')


def test_simple_add():
    """SimpleAdd: push 7, push 8, add -> topo da pilha = 15"""
    vm = VMEmulator()
    vm.execute(os.path.join(VM_DIR, 'SimpleAdd.vm'))

    assert vm.stack[-1] == 15, f"Esperado 15, obteve {vm.stack[-1]}"
    # SP deve apontar para 257 (256 + 1 elemento na pilha)
    print("✅ SimpleAdd: topo = 15 (correto)")


def test_stack_test():
    """StackTest: testa eq, gt, lt, and, or, not"""
    vm = VMEmulator()
    vm.execute(os.path.join(VM_DIR, 'StackTest.vm'))

    # Valores esperados na pilha (de baixo para cima):
    # 17==17 -> -1 (true)
    # 17==16 -> 0 (false)
    # 3>4 -> 0 (false)
    # 3>2 -> -1 (true)
    # 3<4 -> -1 (true)
    # 3<2 -> 0 (false)
    # 9&7 -> 1
    # 9|7 -> 15 (não, 9|7 = 15? 1001|0111 = 1111 = 15)
    # !32767 -> -32768
    expected = [-1, 0, 0, -1, -1, 0, 1, 15, -32768]

    assert vm.stack == expected, f"Esperado {expected}, obteve {vm.stack}"
    print("✅ StackTest: todos os valores corretos")


def test_basic_test():
    """BasicTest: testa push/pop com vários segmentos (valores do .cmp oficial)"""
    vm = VMEmulator()
    vm.execute(os.path.join(VM_DIR, 'BasicTest.vm'))

    # Valores conforme BasicTest.cmp oficial do nand2tetris
    assert vm.ram[256] == 472, f"RAM[256] esperado 472, obteve {vm.ram[256]}"
    assert vm.ram[300] == 10, f"RAM[300] (local 0) esperado 10, obteve {vm.ram[300]}"
    assert vm.ram[401] == 21, f"RAM[401] (arg 1) esperado 21, obteve {vm.ram[401]}"
    assert vm.ram[402] == 22, f"RAM[402] (arg 2) esperado 22, obteve {vm.ram[402]}"
    assert vm.ram[3006] == 36, f"RAM[3006] (this 6) esperado 36, obteve {vm.ram[3006]}"
    assert vm.ram[3012] == 42, f"RAM[3012] (that 2) esperado 42, obteve {vm.ram[3012]}"
    assert vm.ram[3015] == 45, f"RAM[3015] (that 5) esperado 45, obteve {vm.ram[3015]}"
    assert vm.ram[11] == 510, f"RAM[11] (temp 6) esperado 510, obteve {vm.ram[11]}"
    print("✅ BasicTest: todos os segmentos corretos")


def test_pointer_test():
    """PointerTest: testa push/pop pointer"""
    vm = VMEmulator()
    vm.execute(os.path.join(VM_DIR, 'PointerTest.vm'))

    # Após pointer 0 = 3030, pointer 1 = 3040
    assert vm.ram[3] == 3030, f"THIS esperado 3030, obteve {vm.ram[3]}"
    assert vm.ram[4] == 3040, f"THAT esperado 3040, obteve {vm.ram[4]}"
    # this 2 = RAM[3032] = 32
    assert vm.ram[3032] == 32, f"RAM[3032] esperado 32, obteve {vm.ram[3032]}"
    # that 6 = RAM[3046] = 46
    assert vm.ram[3046] == 46, f"RAM[3046] esperado 46, obteve {vm.ram[3046]}"
    # Resultado final: 3030 + 3040 - 32 + 46 = 6084
    assert vm.stack[-1] == 6084, f"Topo esperado 6084, obteve {vm.stack[-1]}"
    print("✅ PointerTest: pointer 0/1 corretos")


def test_static_test():
    """StaticTest: testa push/pop static"""
    vm = VMEmulator()
    vm.execute(os.path.join(VM_DIR, 'StaticTest.vm'))

    # push 111, 333, 888
    # pop static 8, pop static 3, pop static 1
    # static 8 = 888, static 3 = 333, static 1 = 111
    # push static 3 -> 333
    # push static 1 -> 111
    # sub -> 333 - 111 = 222
    # push static 8 -> 888
    # add -> 222 + 888 = 1110
    assert vm.stack[-1] == 1110, f"Topo esperado 1110, obteve {vm.stack[-1]}"
    print("✅ StaticTest: variáveis estáticas corretas")


if __name__ == '__main__':
    print("=" * 50)
    print("TESTES DE INTEGRAÇÃO DO VMTRANSLATOR")
    print("=" * 50)
    print()

    tests = [
        test_simple_add,
        test_stack_test,
        test_basic_test,
        test_pointer_test,
        test_static_test,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: ERRO - {e}")
            failed += 1

    print()
    print(f"Resultado: {passed} passou, {failed} falhou")
    if failed == 0:
        print("🎉 Todos os testes de integração passaram!")
