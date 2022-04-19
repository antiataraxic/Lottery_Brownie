//SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdentryfee;
    address payable public recentWinner;
    AggregatorV3Interface public pricefeed;
    AggregatorV3Interface internal ethusdpricefeed;
    uint256 public randomness;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash;
    event RequestedRandomness(bytes32 requestid);

    constructor(
        address _pricefeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdentryfee = 50 * (10**18);
        ethusdpricefeed = AggregatorV3Interface(_pricefeed);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= get_entrancefee(), "Need to fund more!!");
        players.push(msg.sender);
    }

    function get_entrancefee() public view returns (uint256) {
        (, int256 price, , , ) = ethusdpricefeed.latestRoundData();
        uint256 adjusted_price = uint256(price) * 10**10;
        uint256 costtoenter = (usdentryfee * (10**18)) / adjusted_price;
        return costtoenter;
    }

    function start_lottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't start lottery");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function end_lottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // Alternative but hackable
        //uint256(keccak256(
        //abi.encodePacked
        //(nonce, msg.sender, block.difficulty, block.timestamp))) % players.length
        bytes32 requestid = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestid);
    }

    function fulfillRandomness(bytes32 _requestid, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet"
        );
        require(_randomness > 0, "Random not greater than zero");
        uint256 index_of_winner = _randomness % players.length;
        recentWinner = players[index_of_winner];
        recentWinner.transfer(address(this).balance);

        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
