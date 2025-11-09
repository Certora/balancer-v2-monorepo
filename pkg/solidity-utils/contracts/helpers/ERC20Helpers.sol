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

import "@balancer-labs/v2-interfaces/contracts/solidity-utils/helpers/BalancerErrors.sol";
import "@balancer-labs/v2-interfaces/contracts/solidity-utils/openzeppelin/IERC20.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IAsset.sol";

// solhint-disable

function _asIAsset(IERC20[] memory tokens) pure returns (IAsset[] memory assets) {
    // solhint-disable-next-line no-inline-assembly
    assembly {
        assets := tokens
    }
}

function _sortTokens(
    IERC20 tokenA,
    IERC20 tokenB
) pure returns (IERC20[] memory tokens) {
    bool aFirst = tokenA < tokenB;
    IERC20[] memory sortedTokens = new IERC20[](2 /** @rounds=exact */);

    sortedTokens[0] = aFirst ? tokenA : tokenB;
    sortedTokens[1] = aFirst ? tokenB : tokenA;

    return sortedTokens;
}

function _insertSorted(IERC20[] memory tokens, IERC20 token) pure returns (IERC20[] memory sorted) {
    sorted = new IERC20[](tokens /** @rounds=indeterminate */.length /** @rounds=indeterminate */ + 1 /** @rounds=indeterminate */ /** @rounds=exact */);

    if (tokens /** @rounds=indeterminate */.length /** @rounds=indeterminate */ == 0 /** @rounds=exact */) {
        sorted[0] = token;
        return sorted;
    }

    uint256 i;
    for (i = tokens /** @rounds=indeterminate */.length /** @rounds=indeterminate */; i /** @rounds=indeterminate */ > 0 /** @rounds=exact */ && tokens[i - 1] > token; i--) sorted[i] = tokens[i - 1];
    for (uint256 j = 0 /** @rounds=exact */; j /** @rounds=indeterminate */ < i /** @rounds=indeterminate */; j++) sorted[j] = tokens[j];
    sorted[i] = token;
}

function _findTokenIndex(IERC20[] memory tokens, IERC20 token) pure returns (uint256) {
    // Note that while we know tokens are initially sorted, we cannot assume this will hold throughout
    // the pool's lifetime, as pools with mutable tokens can append and remove tokens in any order.
    uint256 tokensLength = tokens /** @rounds=indeterminate */.length /** @rounds=indeterminate */;
    for (uint256 i = 0 /** @rounds=exact */; i /** @rounds=indeterminate */ < tokensLength /** @rounds=indeterminate */; i++) {
        if (tokens[i] == token) {
            return i /** @rounds=indeterminate */;
        }
    }

    _revert(Errors /** @rounds=indeterminate */.INVALID_TOKEN /** @rounds=indeterminate */);
}
