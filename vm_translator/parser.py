from enum import Enum



class CommandType(Enum):
    C_ARITHMETIC = "C_ARITHMETIC"
    C_PUSH       = "C_PUSH"
    C_POP        = "C_POP"
    C_LABEL      = "C_LABEL"      
    C_GOTO       = "C_GOTO"       
    C_IF         = "C_IF"         
    C_FUNCTION   = "C_FUNCTION"   
    C_CALL       = "C_CALL"       
    C_RETURN     = "C_RETURN"     



ARITHMETIC_COMMANDS = {
    'add', 'sub', 'neg',
    'eq', 'gt', 'lt',
    'and', 'or', 'not'
}


class Parser:
    """Lê e tokeniza comandos de um arquivo .vm"""

    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            self.commands = [
                line.split('//')[0].strip().split()
                for line in f
                if line.strip() and not line.strip().startswith('//')
            ]
            self.commands = [cmd for cmd in self.commands if cmd]
        self.index = 0
        self.current = None

    def has_more_commands(self) -> bool:
        """Indica se há mais comandos para processar."""
        return self.index < len(self.commands)

    def advance(self):
        """Avança para o próximo comando."""
        self.current = self.commands[self.index]
        self.index += 1

    def command_type(self) -> CommandType:
        """Retorna o tipo do comando atual."""
        cmd = self.current[0]
        if cmd in ARITHMETIC_COMMANDS:
            return CommandType.C_ARITHMETIC
        elif cmd == 'push':
            return CommandType.C_PUSH
        elif cmd == 'pop':
            return CommandType.C_POP
        elif cmd == 'label':
            return CommandType.C_LABEL
        elif cmd == 'goto':
            return CommandType.C_GOTO
        elif cmd == 'if-goto':
            return CommandType.C_IF
        elif cmd == 'function':
            return CommandType.C_FUNCTION
        elif cmd == 'call':
            return CommandType.C_CALL
        elif cmd == 'return':
            return CommandType.C_RETURN

    def arg1(self) -> str:
        """Retorna o primeiro argumento do comando atual."""
        if self.command_type() == CommandType.C_ARITHMETIC:
            return self.current[0]
        return self.current[1]

    def arg2(self) -> int:
        """Retorna o segundo argumento (apenas para push, pop, function e call)."""
        return int(self.current[2])

