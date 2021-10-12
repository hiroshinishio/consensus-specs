from eth2spec.test.context import fork_transition_test
from eth2spec.test.helpers.constants import PHASE0, ALTAIR
from eth2spec.test.helpers.fork_transition import (
    do_altair_fork,
    state_transition_across_slots,
    transition_until_fork,
)


@fork_transition_test(PHASE0, ALTAIR, fork_epoch=7)
def test_transition_with_leaking_pre_fork(state, fork_epoch, spec, post_spec, pre_tag, post_tag):
    """
    Leaking starts at epoch 6 (MIN_EPOCHS_TO_INACTIVITY_PENALTY + 2).
    The leaking starts before the fork transition in this case.
    """
    transition_until_fork(spec, state, fork_epoch)

    assert spec.is_in_inactivity_leak(state)
    assert spec.get_current_epoch(state) < fork_epoch

    yield "pre", state

    # irregular state transition to handle fork:
    blocks = []
    state, block = do_altair_fork(state, spec, post_spec, fork_epoch)
    blocks.append(post_tag(block))

    # check post transition state
    assert spec.is_in_inactivity_leak(state)

    # continue regular state transition with new spec into next epoch
    to_slot = post_spec.SLOTS_PER_EPOCH + state.slot
    blocks.extend([
        post_tag(block) for block in
        state_transition_across_slots(post_spec, state, to_slot)
    ])

    yield "blocks", blocks
    yield "post", state


@fork_transition_test(PHASE0, ALTAIR, fork_epoch=6)
def test_transition_with_leaking_at_fork(state, fork_epoch, spec, post_spec, pre_tag, post_tag):
    """
    Leaking starts at epoch 6 (MIN_EPOCHS_TO_INACTIVITY_PENALTY + 2).
    The leaking starts at the fork transition in this case.
    """
    transition_until_fork(spec, state, fork_epoch)

    assert not spec.is_in_inactivity_leak(state)
    assert spec.get_current_epoch(state) < fork_epoch

    yield "pre", state

    # irregular state transition to handle fork:
    blocks = []
    state, block = do_altair_fork(state, spec, post_spec, fork_epoch)
    blocks.append(post_tag(block))

    # check post transition state
    assert spec.is_in_inactivity_leak(state)

    # continue regular state transition with new spec into next epoch
    to_slot = post_spec.SLOTS_PER_EPOCH + state.slot
    blocks.extend([
        post_tag(block) for block in
        state_transition_across_slots(post_spec, state, to_slot)
    ])

    yield "blocks", blocks
    yield "post", state


@fork_transition_test(PHASE0, ALTAIR, fork_epoch=5)
def test_transition_with_leaking_post_fork(state, fork_epoch, spec, post_spec, pre_tag, post_tag):
    """
    Leaking starts at epoch 6 (MIN_EPOCHS_TO_INACTIVITY_PENALTY + 2).
    The leaking starts after the fork transition in this case.
    """
    transition_until_fork(spec, state, fork_epoch)

    assert not spec.is_in_inactivity_leak(state)
    assert spec.get_current_epoch(state) < fork_epoch

    yield "pre", state

    # irregular state transition to handle fork:
    blocks = []
    state, block = do_altair_fork(state, spec, post_spec, fork_epoch)
    blocks.append(post_tag(block))

    # check post transition state
    assert not spec.is_in_inactivity_leak(state)

    # continue regular state transition with new spec into next epoch
    to_slot = post_spec.SLOTS_PER_EPOCH + state.slot
    blocks.extend([
        post_tag(block) for block in
        state_transition_across_slots(post_spec, state, to_slot)
    ])

    # check state again
    assert spec.is_in_inactivity_leak(state)

    yield "blocks", blocks
    yield "post", state
