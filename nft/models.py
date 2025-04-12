from django.db import models

class Item(models.Model):
    token_id = models.IntegerField()  # NFT 토큰 ID
    seller = models.CharField(max_length=42)
    price_klay = models.DecimalField(max_digits=18, decimal_places=6)
    metadata_uri = models.CharField(max_length=255)
    is_listed = models.BooleanField(default=False)

    def to_dict(self):
        return {
            "token_id": self.token_id,
            "seller": self.seller,
            "price_klay": float(self.price_klay),
            "metadata_uri": self.metadata_uri,
            "is_listed": self.is_listed
        }