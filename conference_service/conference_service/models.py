# conference_service/models.py

from django.db import models


class Conference(models.Model):
    acronym = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    held_date = models.DateTimeField()
    submission_deadline = models.DateTimeField()
    review_deadline = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # 如 'preparing', 'submitting', 'reviewing', 'finalizing', 'finished'
    chair_id = models.IntegerField()  # 只存储chair的用户ID
    topics = models.TextField()  # 添加的字段，用于存储主题列表

    def get_topics_list(self):
        """ 返回主题的列表。"""
        return self.topics.split(',')


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    conference_id = models.IntegerField()  # 只存储会议的ID
    invitee_id = models.IntegerField()  # 只存储发送邀请的用户ID
    pc_member_id = models.IntegerField()  # 只存储被邀请的PC member的用户ID
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  # 如 'pending', 'accepted', 'rejected'
    accepted_topics = models.TextField(blank=True)  # 添加的字段，用于存储接受邀请的主题列表
