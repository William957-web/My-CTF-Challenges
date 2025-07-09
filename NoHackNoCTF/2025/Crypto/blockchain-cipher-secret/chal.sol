// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

//Should be blackbox
contract Challenge {
    string private constant FLAG = "UOUJ{flw_jhlzhy_pz_lg_zv_spkpaf}";
    uint8 private constant SHIFT = 7;

    // Encrypt function callable by users
    function encrypt(string memory text) public pure returns (string memory) {
        bytes memory input = bytes(text);
        for (uint i = 0; i < input.length; i++) {
            bytes1 char = input[i];

            if (char >= 0x61 && char <= 0x7A) { // a-z
                input[i] = bytes1(uint8((uint8(char) - 97 + SHIFT) % 26 + 97));
            } else if (char >= 0x41 && char <= 0x5A) { // A-Z
                input[i] = bytes1(uint8((uint8(char) - 65 + SHIFT) % 26 + 65));
            }
            // else: keep digits and punctuation unchanged
        }
        return string(input);
    }

    // Return encrypted FLAG only, without storing plaintext on chain
    function get_flag() public pure returns (string memory) {
        return FLAG;
    }
}