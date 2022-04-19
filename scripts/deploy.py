from scripts.helpful_scripts import fundedwithlink, get_account, get_contract
from brownie import lottery, config, network, accounts
import time


def deploy_lottery():
    account = get_account()
    Lottery = lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
    )
    print("Deployed Lottery!")
    return Lottery


def startlottery():
    account = get_account()
    Lottery = lottery[-1]
    tx1 = Lottery.start_lottery({"from": account})
    tx1.wait(1)
    print("STARTED LOTTERY")


def enterlottery():
    account = get_account()
    Lottery = lottery[-1]
    value = Lottery.get_entrancefee() + 100000000
    tx2 = Lottery.enter({"from": account, "value": value})
    tx2.wait(1)
    print("ENTERED LOTTERY")


def endlottery():
    account = get_account()
    Lottery = lottery[-1]
    tx_fund = fundedwithlink(Lottery.address)
    tx_fund.wait(1)
    tx3 = Lottery.end_lottery({"from": account})
    tx3.wait(1)
    time.sleep(40)
    print(f"{Lottery.recentWinner()} is the new winner!!!")


def main():
    deploy_lottery()
    startlottery()
    enterlottery()
    endlottery()
