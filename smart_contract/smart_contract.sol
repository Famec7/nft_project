// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyNFTMarketplace is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct MarketItem {
        address seller;
        uint256 price;
        bool isListed;
    }

    mapping(uint256 => MarketItem) public marketItems;

    constructor(address initialOwner) ERC721("MyNFT", "MNFT") Ownable(initialOwner) {}

    /// @notice NFT 민팅 (판매는 X)
    function mintWithTokenURI(address to, string memory tokenURI) public onlyOwner returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();

        _mint(to, newTokenId);
        _setTokenURI(newTokenId, tokenURI);

        return newTokenId;
    }

    /// @notice NFT 마켓에 판매 등록
    function listItem(uint256 tokenId, uint256 price) public {
        require(ownerOf(tokenId) == msg.sender, "Not the token owner");
        require(price > 0, "Price must be greater than 0");

        marketItems[tokenId] = MarketItem({
            seller: msg.sender,
            price: price,
            isListed: true
        });
    }

    /// @notice NFT 구매
    function buy(uint256 tokenId) public payable {
        MarketItem memory item = marketItems[tokenId];

        require(item.isListed, "Item not listed for sale");
        require(msg.value >= item.price, "Not enough ETH sent");

        payable(item.seller).transfer(item.price);
        _transfer(item.seller, msg.sender, tokenId);

        marketItems[tokenId].isListed = false;
    }

    /// @notice 판매 정보 확인
    function getListing(uint256 tokenId) public view returns (MarketItem memory) {
        return marketItems[tokenId];
    }
}
