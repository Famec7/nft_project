// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyNFTMarketplace is ERC721URIStorage, Ownable {
    struct MarketItem {
        address seller;
        uint256 price;
    }

    mapping(uint256 => MarketItem) public marketItems;

    constructor(address initialOwner) ERC721("ItemMarket", "Item") Ownable(initialOwner) {}

    /// @notice NFT 민팅 (판매는 X)
    function mintWithTokenURI(address to, uint256 tokenID, string memory tokenURI) public returns (uint256) {
        _mint(to, tokenID);
        _setTokenURI(tokenID, tokenURI);

        return tokenID;
    }

    /// @notice NFT 마켓에 판매 등록
    function listItem(uint256 tokenId, uint256 price, string memory tokenURI) public {
        require(price > 0, "Price must be greater than 0");

        if (!_tokenExists(tokenId)) {
            mintWithTokenURI(owner(), tokenId, tokenURI);
        }
        else {
            require(ownerOf(tokenId) == msg.sender, "Not the token owner");
            _transfer(msg.sender, owner(), tokenId);
        }

        marketItems[tokenId] = MarketItem({
            seller: msg.sender,
            price: price
        });
    }

    /// @notice NFT 구매
    function buy(uint256 tokenId) public payable {
        MarketItem memory item = marketItems[tokenId];

        require(msg.value >= item.price, "Not enough ETH sent");

        payable(item.seller).transfer(item.price);
        _transfer(owner(), msg.sender, tokenId);

        delete marketItems[tokenId];
    }

    /// @notice NFT 판매 등록 취소
    function cancelListing(uint256 tokenId) public {
        MarketItem memory item = marketItems[tokenId];

        require(item.seller == msg.sender, "Only seller can cancel listing");

        delete marketItems[tokenId];
    }

    function _tokenExists(uint256 tokenId) internal view returns (bool) {
        try this.ownerOf(tokenId) returns (address) {
            return true;
        } catch {
            return false;
    }
}
}
