# paper_service/models.py

from django.db import models
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from django.db import models
from django.core.exceptions import ValidationError
# Django 3.1 及以上版本可以直接从 django.db.models 引入 JSONField
from django.db.models import JSONField

class Paper(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=50)
    abstract = models.TextField(max_length=800)
    submission_date = models.DateTimeField(auto_now_add=True)
    pdf = models.CharField(max_length=255, null=True, blank=True)  # 如果是URL或短文本
    conference_id = models.IntegerField()
    author_info = JSONField(default=list)  # 默认为空列表
    topics = JSONField(default=list)   # 存储论文的 topic 信息
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    submitted_by = models.CharField(max_length=255, null=True, blank=True)  # 如果您想存储用户名

    def __str__(self):
        return f"{self.title} (Conference ID: {self.conference_id})"



    def clean(self):
        # 确保至少有一个作者和一个 topic
        if not self.author_info or len(self.author_info) == 0:
            raise ValidationError("At least one author is required.")
        if not self.topics or len(self.topics) == 0:
            raise ValidationError("At least one topic is required.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Review(models.Model):
    conference_id = models.IntegerField(blank=True,null=True)  # 只存储会议的ID
    paper_id = models.IntegerField()  # 只存储论文的ID
    reviewer_id = models.IntegerField()  # 只存储审稿人的用户ID
    score = models.IntegerField(blank=True)
    confidence = models.IntegerField(blank=True)
    comment = models.TextField(blank=True)
    rebuttal = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)  # 如 '已审稿', '待审稿'
    decision = models.CharField(max_length=50, blank=True)  # 如 'accept', 'reject'
