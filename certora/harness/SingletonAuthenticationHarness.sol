import "../munged/solidity-utils/contracts/helpers/SingletonAuthentication.sol";

contract SingletonAuthenticationHarness is SingletonAuthentication {
    constructor(IVault vault) SingletonAuthentication(vault) { }

}