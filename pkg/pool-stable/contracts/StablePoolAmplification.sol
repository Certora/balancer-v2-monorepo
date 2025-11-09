// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.7.0;

import "@balancer-labs/v2-pool-utils/contracts/BasePoolAuthorization.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/WordCodec.sol";

import "./StableMath.sol";

abstract contract StablePoolAmplification is BasePoolAuthorization {
    using WordCodec for bytes32;

    // This contract uses timestamps to slowly update its Amplification parameter over time. These changes must occur
    // over a minimum time period much larger than the blocktime, making timestamp manipulation a non-issue.
    // solhint-disable not-rely-on-time

    // Amplification factor changes must happen over a minimum period of one day, and can at most divide or multiply the
    // current value by 2 every day.
    // WARNING: this only limits *a single* amplification change to have a maximum rate of change of twice the original
    // value daily. It is possible to perform multiple amplification changes in sequence to increase this value more
    // rapidly: for example, by doubling the value every day it can increase by a factor of 8 over three days (2^3).
    uint256 private constant _MIN_UPDATE_TIME = 1 days;
    uint256 private constant _MAX_AMP_UPDATE_DAILY_RATE = 2;

    // The amplification data structure is as follows:
    // [  64 bits |   64 bits  |  64 bits  |   64 bits   ]
    // [ end time | start time | end value | start value ]
    // |MSB                                           LSB|

    uint256 private constant _AMP_START_VALUE_OFFSET = 0;
    uint256 private constant _AMP_END_VALUE_OFFSET = 64;
    uint256 private constant _AMP_START_TIME_OFFSET = 128;
    uint256 private constant _AMP_END_TIME_OFFSET = 192;

    uint256 private constant _AMP_VALUE_BIT_LENGTH = 64;
    uint256 private constant _AMP_TIMESTAMP_BIT_LENGTH = 64;

    bytes32 private _packedAmplificationData;

    event AmpUpdateStarted(uint256 startValue, uint256 endValue, uint256 startTime, uint256 endTime);
    event AmpUpdateStopped(uint256 currentValue);

    constructor(uint256 amplificationParameter) {
        _require(amplificationParameter /** @rounds=indeterminate */ >= StableMath /** @rounds=indeterminate */._MIN_AMP /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.MIN_AMP /** @rounds=indeterminate */);
        _require(amplificationParameter /** @rounds=indeterminate */ <= StableMath /** @rounds=indeterminate */._MAX_AMP /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.MAX_AMP /** @rounds=indeterminate */);

        uint256 initialAmp = Math.mul(amplificationParameter /** @rounds=indeterminate */, StableMath /** @rounds=indeterminate */._AMP_PRECISION /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        _setAmplificationData(initialAmp /** @rounds=indeterminate */);
    }

    function getAmplificationParameter()
        external
        view
        returns (
            uint256 value,
            bool isUpdating,
            uint256 precision
        )
    {
        (value, isUpdating) = _getAmplificationParameter();
        precision = StableMath /** @rounds=indeterminate */._AMP_PRECISION /** @rounds=indeterminate */;
    }

    // Return the current amp value, which will be an interpolation if there is an ongoing amp update.
    // Also return a flag indicating whether there is an ongoing update.
    function _getAmplificationParameter() internal view returns (uint256 value, bool isUpdating) {
        (uint256 startValue, uint256 endValue, uint256 startTime, uint256 endTime) = _getAmplificationData() /** @rounds=indeterminate */;

        // Note that block.timestamp >= startTime, since startTime is set to the current time when an update starts

        if (block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */ < endTime /** @rounds=indeterminate */) {
            isUpdating = true;

            // We can skip checked arithmetic as:
            //  - block.timestamp is always larger or equal to startTime
            //  - endTime is always larger than startTime
            //  - the value delta is bounded by the largest amplification parameter, which never causes the
            //    multiplication to overflow.
            // This also means that the following computation will never revert nor yield invalid results.
            if (endValue /** @rounds=indeterminate */ > startValue /** @rounds=indeterminate */) {
                value = startValue /** @rounds=indeterminate */ + ((endValue /** @rounds=indeterminate */ - startValue /** @rounds=indeterminate */) /** @rounds=indeterminate */ * (block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */ - startTime /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=indeterminate */ / (endTime /** @rounds=indeterminate */ - startTime /** @rounds=indeterminate */) /** @rounds=indeterminate */ /** @rounds=down */ /** @rounds=indeterminate */;
            } else {
                value = startValue /** @rounds=indeterminate */ - ((startValue /** @rounds=indeterminate */ - endValue /** @rounds=indeterminate */) /** @rounds=indeterminate */ * (block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */ - startTime /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=indeterminate */ / (endTime /** @rounds=indeterminate */ - startTime /** @rounds=indeterminate */) /** @rounds=indeterminate */ /** @rounds=down */ /** @rounds=indeterminate */;
            }
        } else {
            isUpdating = false;
            value = endValue /** @rounds=indeterminate */;
        }
    }

    // Unpack and return all amplification-related parameters.
    function _getAmplificationData()
        private
        view
        returns (
            uint256 startValue,
            uint256 endValue,
            uint256 startTime,
            uint256 endTime
        )
    {
        startValue = _packedAmplificationData.decodeUint(_AMP_START_VALUE_OFFSET /** @rounds=indeterminate */, _AMP_VALUE_BIT_LENGTH /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        endValue = _packedAmplificationData.decodeUint(_AMP_END_VALUE_OFFSET /** @rounds=indeterminate */, _AMP_VALUE_BIT_LENGTH /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        startTime = _packedAmplificationData.decodeUint(_AMP_START_TIME_OFFSET /** @rounds=indeterminate */, _AMP_TIMESTAMP_BIT_LENGTH /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        endTime = _packedAmplificationData.decodeUint(_AMP_END_TIME_OFFSET /** @rounds=indeterminate */, _AMP_TIMESTAMP_BIT_LENGTH /** @rounds=indeterminate */) /** @rounds=indeterminate */;
    }

    /**
     * @dev Begin changing the amplification parameter to `rawEndValue` over time. The value will change linearly until
     * `endTime` is reached, when it will be `rawEndValue`.
     *
     * NOTE: Internally, the amplification parameter is represented using higher precision. The values returned by
     * `getAmplificationParameter` have to be corrected to account for this when comparing to `rawEndValue`.
     */
    function startAmplificationParameterUpdate(uint256 rawEndValue, uint256 endTime) external authenticate {
        _require(rawEndValue /** @rounds=indeterminate */ >= StableMath /** @rounds=indeterminate */._MIN_AMP /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.MIN_AMP /** @rounds=indeterminate */);
        _require(rawEndValue /** @rounds=indeterminate */ <= StableMath /** @rounds=indeterminate */._MAX_AMP /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.MAX_AMP /** @rounds=indeterminate */);

        uint256 duration = Math.sub(endTime /** @rounds=indeterminate */, block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */) /** @rounds=down */;
        _require(duration /** @rounds=indeterminate */ >= _MIN_UPDATE_TIME /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.AMP_END_TIME_TOO_CLOSE /** @rounds=indeterminate */);

        (uint256 currentValue, bool isUpdating) = _getAmplificationParameter() /** @rounds=indeterminate */;
        _require(!isUpdating, Errors /** @rounds=indeterminate */.AMP_ONGOING_UPDATE /** @rounds=indeterminate */);

        uint256 endValue = Math.mul(rawEndValue /** @rounds=indeterminate */, StableMath /** @rounds=indeterminate */._AMP_PRECISION /** @rounds=indeterminate */) /** @rounds=indeterminate */;

        // daily rate = (endValue / currentValue) / duration * 1 day
        // We perform all multiplications first to not reduce precision, and round the division up as we want to avoid
        // large rates. Note that these are regular integer multiplications and divisions, not fixed point.
        uint256 dailyRate = endValue /** @rounds=indeterminate */ > currentValue /** @rounds=indeterminate */
            ? Math.divUp(Math.mul(1 days /** @rounds=exact */, endValue /** @rounds=indeterminate */) /** @rounds=indeterminate */, Math.mul(currentValue /** @rounds=indeterminate */, duration /** @rounds=indeterminate */) /** @rounds=indeterminate */)
            : Math.divUp(Math.mul(1 days /** @rounds=exact */, currentValue /** @rounds=indeterminate */) /** @rounds=indeterminate */, Math.mul(endValue /** @rounds=indeterminate */, duration /** @rounds=indeterminate */) /** @rounds=indeterminate */) /** @rounds=indeterminate */;
        _require(dailyRate /** @rounds=indeterminate */ <= _MAX_AMP_UPDATE_DAILY_RATE /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.AMP_RATE_TOO_HIGH /** @rounds=indeterminate */);

        _setAmplificationData(currentValue /** @rounds=indeterminate */, endValue /** @rounds=indeterminate */, block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */, endTime /** @rounds=indeterminate */);
    }

    /**
     * @dev Stops the amplification parameter change process, keeping the current value.
     */
    function stopAmplificationParameterUpdate() external authenticate {
        (uint256 currentValue, bool isUpdating) = _getAmplificationParameter() /** @rounds=indeterminate */;
        _require(isUpdating, Errors /** @rounds=indeterminate */.AMP_NO_ONGOING_UPDATE /** @rounds=indeterminate */);

        _setAmplificationData(currentValue /** @rounds=indeterminate */);
    }

    function _setAmplificationData(uint256 value) private {
        _storeAmplificationData(value /** @rounds=indeterminate */, value /** @rounds=indeterminate */, block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */, block /** @rounds=indeterminate */.timestamp /** @rounds=indeterminate */);
        emit AmpUpdateStopped(value /** @rounds=indeterminate */);
    }

    function _setAmplificationData(
        uint256 startValue,
        uint256 endValue,
        uint256 startTime,
        uint256 endTime
    ) private {
        _storeAmplificationData(startValue /** @rounds=indeterminate */, endValue /** @rounds=indeterminate */, startTime /** @rounds=indeterminate */, endTime /** @rounds=indeterminate */);
        emit AmpUpdateStarted(startValue /** @rounds=indeterminate */, endValue /** @rounds=indeterminate */, startTime /** @rounds=indeterminate */, endTime /** @rounds=indeterminate */);
    }

    function _storeAmplificationData(
        uint256 startValue,
        uint256 endValue,
        uint256 startTime,
        uint256 endTime
    ) private {
        _packedAmplificationData =
            WordCodec.encodeUint(startValue /** @rounds=indeterminate */, _AMP_START_VALUE_OFFSET /** @rounds=indeterminate */, _AMP_VALUE_BIT_LENGTH /** @rounds=indeterminate */) |
            WordCodec.encodeUint(endValue /** @rounds=indeterminate */, _AMP_END_VALUE_OFFSET /** @rounds=indeterminate */, _AMP_VALUE_BIT_LENGTH /** @rounds=indeterminate */) |
            WordCodec.encodeUint(startTime /** @rounds=indeterminate */, _AMP_START_TIME_OFFSET /** @rounds=indeterminate */, _AMP_TIMESTAMP_BIT_LENGTH /** @rounds=indeterminate */) |
            WordCodec.encodeUint(endTime /** @rounds=indeterminate */, _AMP_END_TIME_OFFSET /** @rounds=indeterminate */, _AMP_TIMESTAMP_BIT_LENGTH /** @rounds=indeterminate */);
    }

    // Permissioned functions

    /**
     * @dev Overrides only owner action to allow setting the cache duration for the token rates
     */
    function _isOwnerOnlyAction(bytes32 actionId) internal view virtual override returns (bool) {
        return
            (actionId == getActionId(this.startAmplificationParameterUpdate.selector)) ||
            (actionId == getActionId(this.stopAmplificationParameterUpdate.selector)) ||
            super._isOwnerOnlyAction(actionId);
    }
}
