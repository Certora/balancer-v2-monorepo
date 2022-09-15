pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/pool-stable/contracts/ComposableStablePool.sol";

// This is the contract that is actually verified; it may contain some helper
// methods for the spec to access internal state, or may override some of the
// more complex methods in the original contract.
contract ComposableStablePoolHarness is ComposableStablePool {
    using SafeMath for uint256;
    using StablePoolUserData for bytes;
    enum SwapKind { GIVEN_IN, GIVEN_OUT }

    address sender;
    address recepient;
    IERC20[] tokens;
    address _protocolFeesCollector;
    uint256[] collectedFees;
    // bool public initialized;

    constructor(NewPoolParams memory params) ComposableStablePool(params) {
        require(params.tokens.length==2);
        require(params.rateProviders.length==2);
        require(params.tokenRateCacheDurations.length==2);
        require(params.exemptFromYieldProtocolFeeFlags.length==2);
        // require(!initialized, "for rules");
        // initialized == true;
    }
    // gets join kind
    function getJoinKind(bytes memory userData) public view returns(StablePoolUserData.JoinKind) {
        StablePoolUserData.JoinKind kind = userData.joinKind();
        return kind;
    }
    
    
    // gets action id by selector
    function getActionId(uint32 selector) view public returns (bytes32) {
        return getActionId(bytes4(selector));
    }

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
    ) public override returns (uint256[] memory amounts, uint256[] memory fees) {
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

        _receiveAsset(_token0, sender, amounts[0], fees[0], 0);
        _receiveAsset(_token1, sender, amounts[1], fees[1], 1);
        if (balances.length>2)
            _receiveAsset(_token2, sender, amounts[2], fees[2], 2);
        // else if (balances.length>3)
        //     _receiveAsset(_token3, sender, amounts[3], fees[3]);
        // else if (balances.length>4)
        //     _receiveAsset(_token4, sender, amounts[4], fees[4]);
        // else if (balances.length>5)
        //     _receiveAsset(_token5, sender, amounts[5], fees[5]);
    }

    function _receiveAsset(IERC20 token, address sender, uint256 amount, uint256 fee, uint256 id) public {
        require(token == _token0 || token == _token1 || token == _token2);
        // require(|| token == _token3 || token == _token4 || token == _token5);
        token.transferFrom(sender, address(this), amount);
        if (fee > 0) { // changed so fees stay within this contract
            token.transferFrom(sender, address(this), fee);
            collectedFees[id] += fee;
        }
    }

    function _receiveAsset(uint256 num, address sender, uint256 amount) public {
        if (num == 0) 
        _token0.transferFrom(sender, address(this), amount);
        else if (num == 1) 
            _token1.transferFrom(sender, address(this), amount);
        else if (num == 2) 
            _token2.transferFrom(sender, address(this), amount);
        // else if (num == 3) 
        //     _token3.transferFrom(sender, address(this), amount);
        // else if (num == 4) 
        //     _token4.transferFrom(sender, address(this), amount);
        // else if (num == 5) 
        //     _token5.transferFrom(sender, address(this), amount);
    }
    
    function onExitPool(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) public override returns (uint256[] memory amounts, uint256[] memory fees) {
        require(_getTotalTokens() == balances.length, "length needs to be the same");
        uint256 inputBalance;
        for (uint256 i; i <balances.length; ++i) {
            inputBalance += balances[i];
        }
        require(inputBalance > 0);
        (amounts, fees) = super.onExitPool(
                poolId,
                sender,
                recipient,
                balances,
                lastChangeBlock,
                protocolSwapFeePercentage,
                userData
            );

        _sendAsset(_token0, recipient, amounts[0], fees[0], 0);
        _sendAsset(_token1, recipient, amounts[1], fees[1], 1);
        if (balances.length>2)
            _sendAsset(_token2, recipient, amounts[2], fees[2], 2);
        // else if (balances.length>3)
        //     _sendAsset(_token3, recipient, amounts[3], fees[3]);
        // else if (balances.length>4)
        //     _sendAsset(_token4, recipient, amounts[4], fees[4]);
        // else if (balances.length>5)
        //     _sendAsset(_token5, recipient, amounts[5], fees[5]);
    }
        
    function _sendAsset(IERC20 token, address recipient, uint256 amount, uint256 fee, uint256 id) public {
        require(token == _token0 || token == _token1 || token == _token2);
        // require(token == _token3 || token == _token4 || token == _token5);
        token.transfer(recipient, amount);
        if (fee > 0) {
            collectedFees[id] += fee;
        }
    }

    function _sendAsset(uint256 num, address recipient, uint256 amount) public {
        if (num == 0)
            _token0.transfer(recipient, amount);
        else if (num == 1) 
            _token1.transfer(recipient, amount);
        else if (num == 2) 
            _token2.transfer(recipient, amount);
        // else if (num == 3) 
        //     _token3.transfer(recipient, amount);
        // else if (num == 4) 
        //     _token4.transfer(recipient, amount);
        // else if (num == 5) 
        //     _token5.transfer(recipient, amount);
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

        request = SwapRequest({kind: IVault.SwapKind(_kind), tokenIn: IERC20(address(0)), tokenOut: IERC20(address(0)), amount: _amount, poolId: _poolId, lastChangeBlock: 0, from: address(0), to: address(0), userData: '0'});
        uint256[] memory balances = new uint256[](_getTotalTokens());
        balances[0] = balanceOf(0);
        balances[1] = balanceOf(1);
        balances[2] = balanceOf(2);
        if (_getTotalTokens()>3)
            balances[3] = balanceOf(3);
        if (_getTotalTokens()>4)
            balances[4] = balanceOf(4);
        if (_getTotalTokens()>5)
            balances[5] = balanceOf(5);
        amountCalculated = super.onSwap(request, balances, indexIn, indexOut);

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
        // else if (num==3)
        //     return _token3.balanceOf(address(this));
        // else if (num==4)
        //     return _token4.balanceOf(address(this));
        // else if (num==5)
        //     return _token5.balanceOf(address(this));
    }


    function balanceOf(address owner, uint256 num) public returns (uint256) {        
        if (num==0)
            return _token0.balanceOf(owner);
        else if (num==1)
            return _token1.balanceOf(owner);
        else if (num==2)
            return _token2.balanceOf(owner);
        // else if (num==3)
        //     return _token3.balanceOf(owner);
        // else if (num==4)
        //     return _token4.balanceOf(owner);
        // else if (num==5)
        //     return _token5.balanceOf(owner);
    }

    function totalTokensBalance(address u) public returns (uint256 total) {        
        total = _token0.balanceOf(u);
        total += _token1.balanceOf(u);
        total += _token2.balanceOf(u);
        // total += _token3.balanceOf(u);
        // total += _token4.balanceOf(u);
        // total += _token5.balanceOf(u);
        total -= this.balanceOf(address(this));
    }

    function totalTokensBalance() public view returns (uint256 total) {        
        total = _token0.balanceOf(address(this));
        total = total.add(_token1.balanceOf(address(this)));
        total = total.add(_token2.balanceOf(address(this)));
    }

    function getToken(uint256 num) public returns (address) {
        if (num==0) return address(_token0);
        if (num==1) return address(_token1);
        if (num==2) return address(_token2);
        // if (num==3) return address(_token3);
        // if (num==4) return address(_token4);
        // if (num==5) return address(_token5);

         _revert(Errors.INVALID_TOKEN);
    }

    function requireOrder(address e_sender) public {
        require (e_sender < address(_token0));
        require (address(_token0)<address(_token1) && address(_token1)<address(_token2));
        // require (address(_token2)<address(_token3) && address(_token3)<address(_token4) && address(_token4)<address(_token5));
        require (getTotalTokens()>2 && getTotalTokens()<=3);
        require (getBptIndex() < getTotalTokens());
        require (address(this) == address(getToken(getBptIndex())));
    }

    function getTotalTokens() public view returns (uint256) {
        return _getTotalTokens();
    }
    function minAmp() public pure returns (uint256) {
        return StableMath._MIN_AMP;
    }

    function maxAmp() public pure returns (uint256) {
        return StableMath._MAX_AMP;
    }

    function AMP_PRECISION() public pure returns (uint256) {
        return StableMath._AMP_PRECISION;
    }
}