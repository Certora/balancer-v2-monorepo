pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/pool-stable/contracts/StablePool.sol";

// This is the contract that is actually verified; it may contain some helper
// methods for the spec to access internal state, or may override some of the
// more complex methods in the original contract.
contract StablePoolHarness is StablePool {
    enum SwapKind { GIVEN_IN, GIVEN_OUT }

    address sender;
    address recepient;
    IERC20[] tokens;
    address _protocolFeesCollector;

    constructor(
        IVault vault,
        string memory name,
        string memory symbol,
        IERC20[] memory tokens, 
        uint256 amplificationParameter,
        uint256 swapFeePercentage,
        uint256 pauseWindowDuration,
        uint256 bufferPeriodDuration,
        address owner
    ) StablePool(vault, name, symbol, tokens, amplificationParameter, 
    swapFeePercentage, pauseWindowDuration, bufferPeriodDuration, owner) {}
    
    // sets recovery mode on or off
    function setRecoveryMode(bool enabled) public {
        _setRecoveryMode(enabled);
    }

    function onJoinPool(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) public override returns (uint256[] memory, uint256[] memory) {
        uint256[] memory amounts;
        uint256[] memory fees;
        require(_getTotalTokens() == balances.length, "length needs to be the same");
        (amounts, fees) = super.onJoinPool(
            poolId,
            sender,
            recipient,
            balances,
            lastChangeBlock,
            protocolSwapFeePercentage,
            userData
        );

        _receiveAsset(_token0, sender, amounts[0], fees[0]);
        _receiveAsset(_token1, sender, amounts[1], fees[1]);
        if (balances.length>2)
            _receiveAsset(_token2, sender, amounts[2], fees[2]);
        else if (balances.length>3)
            _receiveAsset(_token3, sender, amounts[3], fees[3]);
        else if (balances.length>4)
            _receiveAsset(_token4, sender, amounts[4], fees[4]);
    }


    function _receiveAsset(IERC20 token, address sender, uint256 amount, uint256 fee) public {
        token.transferFrom(sender, address(this), amount);
        if (fee > 0) {
            token.transfer(_protocolFeesCollector, fee);
        }
    }

    function _receiveAsset(uint256 num, address sender, uint256 amount) public {
        if (num == 0) 
        _token0.transferFrom(sender, address(this), amount);
        else if (num == 1) 
            _token1.transferFrom(sender, address(this), amount);
        else if (num == 2) 
            _token2.transferFrom(sender, address(this), amount);
        else if (num == 3) 
            _token3.transferFrom(sender, address(this), amount);
        else if (num == 4) 
            _token4.transferFrom(sender, address(this), amount);
    }
    
    function onExitPool(
            bytes32 poolId,
            address sender,
            address recipient,
            uint256[] memory balances,
            uint256 lastChangeBlock,
            uint256 protocolSwapFeePercentage,
            bytes memory userData
        ) public override returns (uint256[] memory, uint256[] memory) {
            uint256[] memory amounts;
            uint256[] memory fees;
            require(_getTotalTokens() == balances.length, "length needs to be the same");
        (amounts, fees) = super.onExitPool(
                poolId,
                sender,
                recipient,
                balances,
                lastChangeBlock,
                protocolSwapFeePercentage,
                userData
            );

        _sendAsset(_token0, recipient, amounts[0], fees[0]);
        _sendAsset(_token1, recipient, amounts[1], fees[1]);
        if (balances.length>2)
            _sendAsset(_token2, recipient, amounts[2], fees[2]);
        else if (balances.length>3)
            _sendAsset(_token3, recipient, amounts[3], fees[3]);
        else if (balances.length>4)
            _sendAsset(_token4, recipient, amounts[4], fees[4]);
    }
        
    function _sendAsset(IERC20 token, address recipient, uint256 amount, uint256 fee) public {
        token.transfer(recipient, amount);
        if (fee > 0) {
            token.transfer(_protocolFeesCollector, fee);
        }
    }

    function _sendAsset(uint256 num, address recipient, uint256 amount) public {
        if (num == 0)
            _token0.transfer(recipient, amount);
        else if (num == 1) 
            _token1.transfer(recipient, amount);
        else if (num == 2) 
            _token2.transfer(recipient, amount);
        else if (num == 3) 
            _token3.transfer(recipient, amount);
        else if (num == 4) 
            _token4.transfer(recipient, amount);
    }

    function onSwap(
        uint8 _kind, // 0: IVault.SwapKind.GIVEN_IN, 1: IVault.SwapKind.GIVEN_OUT, 
        uint256 _amount, // used in both
        bytes32 _poolId, // used in both            
        uint256 indexIn,
        uint256 indexOut
    ) public returns (uint256) {
        SwapRequest memory request;
        uint256 amountGiven;
        uint256 amountCalculated;
        uint256 amountIn;
        uint256 amountOut;

        if (_getTotalTokens()==2) {
            request = SwapRequest({kind: IVault.SwapKind(_kind), tokenIn: IERC20(address(0)), tokenOut: IERC20(address(0)), amount: _amount, poolId: _poolId, lastChangeBlock: 0, from: address(0), to: address(0), userData: '0'});
            super.onSwap(request, balanceOf(indexIn), balanceOf(indexOut));
        } else {
            request = SwapRequest({kind: IVault.SwapKind(_kind), tokenIn: IERC20(address(0)), tokenOut: IERC20(address(0)), amount: _amount, poolId: _poolId, lastChangeBlock: 0, from: address(0), to: address(0), userData: '0'});
            uint256[] memory balances = new uint256[](_getTotalTokens());
            balances[0] = balanceOf(0);
            balances[1] = balanceOf(1);
            balances[2] = balanceOf(2);
            if (_getTotalTokens()>3)
                balances[3] = balanceOf(3);
            if (_getTotalTokens()>4)
                balances[4] = balanceOf(4);
            amountCalculated = super.onSwap(request, balances, indexIn, indexOut);
        }
        if (SwapKind(_kind) == SwapKind.GIVEN_IN) {
            (amountIn, amountOut) = (amountGiven, amountCalculated);
        } else {
            (amountIn, amountOut) = (amountCalculated, amountGiven);
        }
        _receiveAsset(indexIn, sender, amountIn);
        _sendAsset(indexOut, recepient, amountOut);
    }

    function balanceOf(uint256 num) public returns (uint256) {
        if (num==0)
            return _token0.balanceOf(address(this));
        else if (num==1)
            return _token1.balanceOf(address(this));
        else if (num==2)
            return _token2.balanceOf(address(this));
        else if (num==3)
            return _token3.balanceOf(address(this));
        else if (num==4)
            return _token4.balanceOf(address(this));
    }


    function totalTokensBalance() public returns (uint256 total) {        
        total = _token0.balanceOf(address(this));
        total += _token1.balanceOf(address(this));
        total += _token2.balanceOf(address(this));
        total += _token3.balanceOf(address(this));
        total += _token4.balanceOf(address(this));
    }

    function getToken0() public returns (address) {
        return address(_token0);
    }
    function getToken1() public returns (address) {
        return address(_token1);
    }
    function getToken2() public returns (address) {
        return address(_token2);
    }
    function getToken3() public returns (address) {
        return address(_token3);
    }
    function getToken4() public returns (address) {
        return address(_token4);
    }
    function getTotalTokens() public view returns (uint256) {
        return _getTotalTokens();
    }

}