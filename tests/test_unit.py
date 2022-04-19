from brownie import accounts, config, network, exceptions
from scripts.deploy import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fundedwithlink,
    get_account,
    get_contract,
)
import pytest


def test_expected_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    expected_entrfee = 2500000000000000000
    entrfee = lottery.get_entrancefee()

    assert entrfee == expected_entrfee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.get_entrancefee()})


def test_can_enter_and_start():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.get_entrancefee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.get_entrancefee()})
    fundedwithlink(lottery)
    lottery.end_lottery({"from": account})
    assert lottery.LOTTERY_STATE == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.start_lottery({"from": account})
    lottery.enter({"from": get_account(index=1), "value": lottery.get_entrancefee()})
    lottery.enter({"from": account, "value": lottery.get_entrancefee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.get_entrancefee()})
    fundedwithlink(lottery)
    transaction = lottery.end_lottery({"from": account})
    requestId = transaction.events["RequestedRandomness"]["requestid"]
    static_rng = 7
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, static_rng, lottery.address, {"from": account}
    )
    lottbalnce = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == account.balance() + lottbalnce
