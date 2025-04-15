// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MyNFTMarketplace is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    struct MarketItem {
        address seller;
        uint256 price;
    }

    mapping(uint256 => MarketItem) public marketItems;

    IERC20 public kaiaToken;

    event Minted(address indexed to, uint256 tokenId, string uri);

    constructor(address initialOwner) ERC721("ItemMarket", "Item") Ownable(initialOwner) {}

    /// @notice Klip 주소 지정
    function setKaiaTokenAddress(address _kaiaTokenAddress) public onlyOwner {
        require(_kaiaTokenAddress != address(0), "Invalid address");
        kaiaToken = IERC20(_kaiaTokenAddress);
    }

    /// @notice NFT 민팅 (판매는 X)
    function mintWithTokenURI(address to, string memory tokenURI) public returns (uint256) {
         uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _mint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        emit Minted(to, tokenId, tokenURI);

        return tokenId;
    }

    /// @notice NFT 마켓에 판매 등록
    function listItem(uint256 tokenId, uint256 price, string memory tokenURI, address seller) public {
        require(price > 0, "Price must be greater than 0");

        if (!_tokenExists(tokenId)) {
            tokenId = mintWithTokenURI(owner(), tokenURI);
        }
        else {
            require(ownerOf(tokenId) == seller, "Not the token owner");
            _transfer(seller, owner(), tokenId);
        }

        marketItems[tokenId] = MarketItem({
            seller: seller,
            price: price
        });
    }

    /// @notice NFT 구매
    function buy(uint256 tokenId) public payable {
        MarketItem memory item = marketItems[tokenId];

        // 토큰 승인 확인
        uint256 allowance = kaiaToken.allowance(msg.sender, address(this));
        require(allowance >= item.price, "Insufficient allowance to purchase NFT");

        require(kaiaToken.transferFrom(msg.sender, item.seller, item.price), "Payment failed");
        _transfer(owner(), msg.sender, tokenId);

        delete marketItems[tokenId];
    }

    /// @notice NFT 판매 등록 취소
    function cancelListing(uint256 tokenId) public {
        MarketItem memory item = marketItems[tokenId];

        _transfer(owner(), item.seller, tokenId);
        item.price = 0;

        delete marketItems[tokenId];
    }

    /// @notice NFT 삭제
    function burn(uint256 tokenID) public {
        require(_tokenExists(tokenID), "Token does not exist");
        
        _burn(tokenID);
    }

    function _tokenExists(uint256 tokenId) internal view returns (bool) {
        try this.ownerOf(tokenId) returns (address) {
            return true;
        } catch {
            return false;
        }
    }
}
