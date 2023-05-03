pragma solidity ^0.7.0;

contract Receiver {
    fallback() external payable { }

    bytes returndata;
    function sendTo() external payable returns (bool, bytes memory) { return (true, returndata); }

    receive() external payable { }
}