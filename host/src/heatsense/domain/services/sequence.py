"""Sequence number delta calculation with uint32 modular arithmetic.

Sequence counters on wire frames are 32-bit unsigned integers (0 to 2^32 - 1)
that increment on each emitted frame. This module computes gaps and detects
duplicates or reordered frames across the uint32 boundary.
"""

from heatsense.domain.value_objects.frames import SeqDelta, SeqDeltaKind

UINT32_MODULUS: int = 1 << 32
HALF_UINT32: int = 1 << 31


def seq_gap(prev_seq: int, new_seq: int) -> SeqDelta:
    """Compute sequence delta between consecutive received frames.

    Args:
        prev_seq: Previous frame sequence counter (uint32).
        new_seq: Current frame sequence counter (uint32).

    Returns:
        SeqDelta classifying the transition as IN_ORDER, GAP, or DUPLICATE_OR_REORDER.
    """
    diff = (new_seq - prev_seq) % UINT32_MODULUS

    if diff == 1:
        return SeqDelta(kind=SeqDeltaKind.IN_ORDER, lost_count=0)

    if 1 < diff < HALF_UINT32:
        return SeqDelta(kind=SeqDeltaKind.GAP, lost_count=diff - 1)

    return SeqDelta(kind=SeqDeltaKind.DUPLICATE_OR_REORDER, lost_count=0)
