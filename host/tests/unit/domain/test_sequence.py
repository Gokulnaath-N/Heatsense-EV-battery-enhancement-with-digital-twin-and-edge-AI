"""Unit tests for sequence gap and wrap-around detection."""

from heatsense.domain.services.sequence import HALF_UINT32, UINT32_MODULUS, seq_gap
from heatsense.domain.value_objects.frames import SeqDeltaKind


def test_seq_gap_in_order() -> None:
    res = seq_gap(10, 11)
    assert res.kind == SeqDeltaKind.IN_ORDER
    assert res.lost_count == 0


def test_seq_gap_wraparound_in_order() -> None:
    res = seq_gap(UINT32_MODULUS - 1, 0)
    assert res.kind == SeqDeltaKind.IN_ORDER
    assert res.lost_count == 0


def test_seq_gap_normal_gap() -> None:
    res = seq_gap(10, 15)
    assert res.kind == SeqDeltaKind.GAP
    assert res.lost_count == 4


def test_seq_gap_wraparound_gap() -> None:
    # 0xFFFFFFFE -> 0: missing 0xFFFFFFFF (lost 1)
    res = seq_gap(UINT32_MODULUS - 2, 0)
    assert res.kind == SeqDeltaKind.GAP
    assert res.lost_count == 1

    # 0xFFFFFFFE -> 1: missing 0xFFFFFFFF, 0 (lost 2)
    res2 = seq_gap(UINT32_MODULUS - 2, 1)
    assert res2.kind == SeqDeltaKind.GAP
    assert res2.lost_count == 2


def test_seq_gap_duplicate() -> None:
    res = seq_gap(42, 42)
    assert res.kind == SeqDeltaKind.DUPLICATE_OR_REORDER
    assert res.lost_count == 0


def test_seq_gap_reorder() -> None:
    res = seq_gap(42, 41)
    assert res.kind == SeqDeltaKind.DUPLICATE_OR_REORDER
    assert res.lost_count == 0


def test_seq_gap_large_jump_boundary() -> None:
    # diff just below HALF_UINT32 is considered a huge gap
    res_gap = seq_gap(0, HALF_UINT32 - 1)
    assert res_gap.kind == SeqDeltaKind.GAP
    assert res_gap.lost_count == HALF_UINT32 - 2

    # diff at or above HALF_UINT32 is considered backward / duplicate / reorder
    res_reorder = seq_gap(0, HALF_UINT32)
    assert res_reorder.kind == SeqDeltaKind.DUPLICATE_OR_REORDER
    assert res_reorder.lost_count == 0
