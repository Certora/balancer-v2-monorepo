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

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/openzeppelin/IERC20.sol";
import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";

library InputHelpers {
    function ensureInputLengthMatch(uint256 a, uint256 b) internal pure {
        _require(a /** @rounds=indeterminate */ == b /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.INPUT_LENGTH_MISMATCH /** @rounds=indeterminate */);
    }

    function ensureInputLengthMatch(
        uint256 a,
        uint256 b,
        uint256 c
    ) internal pure {
        _require(a /** @rounds=indeterminate */ == b /** @rounds=indeterminate */ && b /** @rounds=indeterminate */ == c /** @rounds=indeterminate */, Errors /** @rounds=indeterminate */.INPUT_LENGTH_MISMATCH /** @rounds=indeterminate */);
    }

    function ensureArrayIsSorted(IERC20[] memory array) internal pure {
        address[] memory addressArray;
        // solhint-disable-next-line no-inline-assembly
        assembly {
            addressArray := array
        }
        ensureArrayIsSorted(addressArray);
    }

    function ensureArrayIsSorted(address[] memory array) internal pure {
        if (array /** @rounds=indeterminate */.length /** @rounds=indeterminate */ < 2 /** @rounds=exact */) {
            return;
        }

        address previous = array[0];
        for (uint256 i = 1 /** @rounds=exact */; i /** @rounds=indeterminate */ < array /** @rounds=indeterminate */.length /** @rounds=indeterminate */; ++i) {
            address current = array[i];
            _require(previous < current, Errors /** @rounds=indeterminate */.UNSORTED_ARRAY /** @rounds=indeterminate */);
            previous = current;
        }
    }
}
