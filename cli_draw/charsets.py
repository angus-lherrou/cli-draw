class Charset:
    _chars: str

    def val2char(self, val):
        return self._chars[val]

    def char2val(self, char):
        return self._chars.index(char)


class SingleBox(Charset):
    _chars = " ╷╴┐╵│┘┤╶┌─┬└├┴┼"


class AsciiBox(Charset):
    _chars = r" i>,!|`{</-v\}^+"


# VAL2CHAR = [
#     ' ',  # 0b0000
#     '╷',  # 0b0001
#     '╴',  # 0b0010
#     '┐',  # 0b0011
#     '╵',  # 0b0100
#     '│',  # 0b0101
#     '┘',  # 0b0110
#     '┤',  # 0b0111
#     '╶',  # 0b1000
#     '┌',  # 0b1001
#     '─',  # 0b1010
#     '┬',  # 0b1011
#     '└',  # 0b1100
#     '├',  # 0b1101
#     '┴',  # 0b1110
#     '┼',  # 0b1111
# ]
# CHAR2VAL = {
#     ' ': 0b0000,
#     '╷': 0b0001,
#     '╴': 0b0010,
#     '┐': 0b0011,
#     '╵': 0b0100,
#     '│': 0b0101,
#     '┘': 0b0110,
#     '┤': 0b0111,
#     '╶': 0b1000,
#     '┌': 0b1001,
#     '─': 0b1010,
#     '┬': 0b1011,
#     '└': 0b1100,
#     '├': 0b1101,
#     '┴': 0b1110,
#     '┼': 0b1111,
# }
