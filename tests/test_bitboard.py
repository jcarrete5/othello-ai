from othelloai import bitboard as bb


def test_directions():
    needed_directions = frozenset({"n", "ne", "e", "se", "s", "sw", "w", "nw"})
    for dir_ in bb.DIRECTIONS:
        assert dir_ in needed_directions


def test_pos_mask():
    assert bb.pos_mask(0, 0) == 0x8000000000000000
    assert bb.pos_mask(7, 7) == 0x0000000000000001
    assert bb.pos_mask(0, 7) == 0x0100000000000000
    assert bb.pos_mask(7, 0) == 0x0000000000000080
    assert bb.pos_mask(4, 4) == 0x0000000008000000


def test_shift_n():
    mask = 0x0000800000000000
    assert bb.shift(mask, "n") == 0x0080000000000000
    assert bb.shift(mask, "n", times=2) == 0x8000000000000000


def test_shift_ne():
    mask = 0x0000001000000000
    assert bb.shift(mask, "ne") == 0x0000080000000000
    assert bb.shift(mask, "ne", times=2) == 0x0004000000000000


def test_shift_e():
    mask = 0x0000001000000000
    assert bb.shift(mask, "e") == 0x0000000800000000
    assert bb.shift(mask, "e", times=2) == 0x0000000400000000


def test_shift_se():
    mask = 0x0000001000000000
    assert bb.shift(mask, "se") == 0x0000000008000000
    assert bb.shift(mask, "se", times=2) == 0x0000000000040000


def test_shift_s():
    mask = 0x0000001000000000
    assert bb.shift(mask, "s") == 0x0000000010000000
    assert bb.shift(mask, "s", times=2) == 0x0000000000100000


def test_shift_sw():
    mask = 0x0000001000000000
    assert bb.shift(mask, "sw") == 0x0000000020000000
    assert bb.shift(mask, "sw", times=2) == 0x0000000000400000


def test_shift_w():
    mask = 0x0000001000000000
    assert bb.shift(mask, "w") == 0x0000002000000000
    assert bb.shift(mask, "w", times=2) == 0x0000004000000000


def test_shift_nw():
    mask = 0x0000001000000000
    assert bb.shift(mask, "nw") == 0x0000200000000000
    assert bb.shift(mask, "nw", times=2) == 0x0040000000000000


def test_shift_oob():
    assert bb.shift(0x80000000C0000000, "w", times=20) == 0
    assert bb.shift(0x0000000000A00001, "e", times=20) == 0
    assert bb.shift(0x1000000000000000, "n", times=20) == 0
    assert bb.shift(0x0000000030000001, "s", times=20) == 0


def test_edge_detection():
    assert bb.on_edge(0x1000000000000000) == "n"
    assert bb.on_edge(0x0100000000000000) in {"ne", "en"}
    assert bb.on_edge(0x0001000000000000) == "e"
    assert bb.on_edge(0x0000000000000001) in {"se", "es"}
    assert bb.on_edge(0x0000000000000010) == "s"
    assert bb.on_edge(0x0000000000000080) in {"sw", "ws"}
    assert bb.on_edge(0x0080000000000000) == "w"
    assert bb.on_edge(0x8000000000000000) in {"nw", "wn"}


def test_dilate():
    assert bb.dilate(0x1000000000000000, "w") == 0x3000000000000000
    assert bb.dilate(0x1000000000000000, "w", times=2) == 0x7000000000000000


def test_not():
    assert bb.not_(0x5555555555555555) == 0xAAAAAAAAAAAAAAAA


def test_to_list():
    assert bb.to_list(0x0100010001000100) == [
        bb.Position(0, 7),
        bb.Position(2, 7),
        bb.Position(4, 7),
        bb.Position(6, 7),
    ]
