import requests
import random

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Conference, Invitation

from .serializers import ConferenceSerializer, InvitationSerializer


class ConferenceListView(APIView):
    def get(self, request, format=None):
        user_id = request.query_params.get('user_id')
        status = request.query_params.get('status')

        if user_id:
            conferences = Conference.objects.filter(chair_id=user_id)
        elif status:
            conferences = Conference.objects.filter(status=status)
        else:
            conferences = Conference.objects.all()

        serializer = ConferenceSerializer(conferences, many=True)
        return Response(serializer.data)


# 用户创建conference
class ConferenceCreateView(APIView):
    def post(self, request, format=None):
        serializer = ConferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员审批conference
class ApproveRejectConferenceView(APIView):
    def post(self, request, format=None):
        conference_id = request.data.get('conference_id')
        action = request.data.get('action')
        conference = get_object_or_404(Conference, id=conference_id)
        if action == 'approve':
            conference.status = 'approved'
        elif action == 'reject':
            conference.status = 'rejected'
        conference.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)


# 根据conference_id获取conference
class ConferenceDetailView(APIView):
    def get(self, request, format=None):
        conference_id = request.query_params.get('conference_id')
        conference = Conference.objects.get(id=conference_id)
        serializer = ConferenceSerializer(conference)
        return Response(serializer.data)


class ConferenceStatusUpdateView(APIView):
    def post(self, request, format=None):
        conference_id = request.data.get('id')
        new_status = request.data.get('status')
        print("new_status: ", new_status)

        try:
            conference = Conference.objects.get(id=conference_id)

            if new_status == 'reviewing':
                # 检查是否至少有两名PC成员接受了审稿邀请
                accepted_invitations = Invitation.objects.filter(conference_id=conference_id, status='accepted').count()
                if accepted_invitations < 2:
                    return Response({'error': '至少需要两名PC成员接受审稿邀请才能开始审稿'}, status=status.HTTP_400_BAD_REQUEST)

            conference.status = new_status
            conference.save()
            return Response({'msg': '会议状态更新成功'}, status=status.HTTP_200_OK)
        except Conference.DoesNotExist:
            return Response({'error': '会议不存在'}, status=status.HTTP_404_NOT_FOUND)


# 分配审稿人给conference
class ConferenceAllocateView(APIView):
    def post(self, request, format=None):
        conference_id = request.data.get('conference_id')

        # 获取该会议的所有接受邀请的PC成员
        pc_members = list(Invitation.objects.filter(conference_id=conference_id, status='accepted').values_list('pc_member_id', flat=True))

        if len(pc_members) < 3:
            return Response({'error': '需要至少3名PC成员进行审稿'}, status=status.HTTP_400_BAD_REQUEST)

        # 从Paper服务获取该会议的所有稿件
        papers_response = requests.get(f'http://localhost:8003/papers/?conference_id={conference_id}')
        if papers_response.status_code != 200:
            return Response({'error': '无法获取稿件信息'}, status=status.HTTP_400_BAD_REQUEST)

        papers = papers_response.json()

        # 随机分配每篇稿件给3名不同的PC成员
        for paper in papers:
            # 检查是否已经有分配的审稿人
            existing_reviews = requests.get(f'http://localhost:8003/reviews/?paper_id={paper["id"]}')
            if existing_reviews.status_code != 200 or len(existing_reviews.json()) >= 3:
                continue  # 如果已经有审稿人或无法获取审稿信息，则跳过此论文

            selected_reviewers = random.sample(pc_members, 3)
            for reviewer_id in selected_reviewers:
                review_data = {
                    'paper_id': paper['id'],
                    'reviewer_id': reviewer_id,
                    'score': 0,
                    'comment': '',
                    'decision': ''
                }
                review_response = requests.post('http://localhost:8003/reviews/create/', json=review_data)
                if review_response.status_code != 201:
                    return Response({'error': '审稿分配失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': '分配成功'}, status=status.HTTP_200_OK)


# Invitation

class InvitationStatusAPIView(APIView):
    def get(self, request, format=None):
        conference_id = request.query_params.get('conference_id')
        invitee_id = request.query_params.get('invitee_id')
        pc_member_id = request.query_params.get('pc_member_id')

        try:
            invitation = Invitation.objects.get(conference_id=conference_id, invitee_id=invitee_id, pc_member_id=pc_member_id)
            status = invitation.status
        except Invitation.DoesNotExist:
            status = '未邀请'

        return Response({'status': status})


class InvitationCreateView(APIView):
    def post(self, request, format=None):
        # 假设前端发送了一个邀请列表
        for invitation_data in request.data:
            serializer = InvitationSerializer(data=invitation_data)
            if serializer.is_valid():
                serializer.save()
            else:
                # 打印具体的错误信息
                print("Validation errors: ", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Invitations created successfully'}, status=status.HTTP_201_CREATED)


class UserInvitationsAPIView(APIView):
    def get(self, request, format=None):
        user_id = request.query_params.get('user_id')
        invitations = Invitation.objects.filter(pc_member_id=user_id)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)


class AcceptInvitationView(APIView):
    def post(self, request, format=None):
        invitation_id = request.data.get('invitation_id')
        try:
            invitation = Invitation.objects.get(id=invitation_id)
            invitation.status = 'accepted'
            invitation.save()
            return Response({'message': 'Invitation accepted'}, status=status.HTTP_200_OK)
        except Invitation.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)


class RejectInvitationView(APIView):
    def post(self, request, format=None):
        invitation_id = request.data.get('invitation_id')
        try:
            invitation = Invitation.objects.get(id=invitation_id)
            invitation.status = 'rejected'
            invitation.save()
            return Response({'message': 'Invitation rejected'}, status=status.HTTP_200_OK)
        except Invitation.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)


# end -----
class ApproveRejectInvitationView(APIView):
    """
    API视图，用于接受或拒绝邀请。
    """

    def post(self, request, format=None):
        invitation_id = request.data.get('invitation_id')
        action = request.data.get('action')
        topics = request.data.get('topics', [])  # 获取传入的topics，如果不存在则默认为空列表

        invitation = get_object_or_404(Invitation, id=invitation_id)

        # 根据请求的操作更新邀请状态
        if action == 'approve':
            invitation.status = 'approved'
            invitation.accepted_topics = ','.join(topics)
        elif action == 'reject':
            invitation.status = 'rejected'
        invitation.save()

        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class InvitationStatusUpdateView(APIView):
    """
    API视图，用于更新邀请的状态。
    """

    def post(self, request, format=None):
        invitation_id = request.data.get('id')
        new_status = request.data.get('status')

        try:
            invitation = Invitation.objects.get(id=invitation_id)
            invitation.status = new_status
            invitation.save()
            return Response({'msg': '邀请更新成功'}, status=status.HTTP_200_OK)
        except Invitation.DoesNotExist:
            return Response({'error': '邀请不存在'}, status=status.HTTP_404_NOT_FOUND)
