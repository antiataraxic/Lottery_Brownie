from brownie import network
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fundedwithlink,
    get_account,
)
from scripts.deploy import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account(id="lotteryacc")
    lottery.start_lottery({"from": account})
    lottery.enter({"from": account, "value": lottery.get_entrancefee()})
    lottery.enter({"from": get_account(), "value": lottery.get_entrancefee()})
    lottery.enter({"from": get_account(), "value": lottery.get_entrancefee()})
    fundedwithlink(lottery)
    lottery.end_lottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
