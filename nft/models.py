from django.db import models

class Item(models.Model):

    item_id = models.AutoField(primary_key=True)  # 아이템 ID
    token_id = models.IntegerField()  # NFT 토큰 ID
    item_name = models.CharField(max_length=100)  # 아이템 이름
    item_value = models.IntegerField(default=0)  # 상점 판매 가치
    item_icon = models.URLField(upload_to='item_icons/', blank=True, null=True)  # 아이템 아이콘 (이미지 파일)

    created_at = models.DateTimeField(auto_now_add=True)  # 생성 날짜

    def __str__(self):
        return self.item_name