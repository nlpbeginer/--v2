# views.py

import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from .serializers import PaperSerializer, ReviewSerializer
from .models import Paper, Review
import random

class PaperSubmissionView(APIView):
    def post(self, request, format=None):
        serializer = PaperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaperListView(APIView):
    def get(self, request, format=None):
        conference_id = request.query_params.get('conference_id')

        if not conference_id:
            return Response({'error': '缺少conference_id参数'}, status=status.HTTP_400_BAD_REQUEST)

        papers = Paper.objects.filter(conference_id=conference_id)

        serializer = PaperSerializer(papers, many=True)
        return Response(serializer.data)


class ReviewListView(APIView):
    """
    API视图，用于根据paper_id获取审稿记录。
    """

    def get(self, request, format=None):
        paper_id = request.query_params.get('paper_id')
        reviewer_id = request.query_params.get('reviewer_id')

        if not paper_id:
            return Response({'error': '缺少paper_id参数'}, status=status.HTTP_400_BAD_REQUEST)

        if reviewer_id:
            reviews = Review.objects.filter(paper_id=paper_id, reviewer_id=reviewer_id)
        else:
            reviews = Review.objects.filter(paper_id=paper_id)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 新建一个review记录，用户稿件分配流程
class NewReviewsView(APIView):
    def post(self, request, format=None):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 更新review信息，即提交审稿记录

class UpdateReviewAPI(APIView):
    def post(self, request, format=None):
        # 检查请求数据是否为列表
        if isinstance(request.data, list):
            # 处理每个元素
            for item in request.data:
                review_id = item.get('id')
                rebuttal = item.get('rebuttal')
                # 找到对应的Review实例
                try:
                    review = Review.objects.get(id=review_id)
                    review.rebuttal = rebuttal
                    review.save()
                except Review.DoesNotExist:
                    # 如果找不到对应的Review实例，返回错误
                    return Response({'error': f'Review with id {review_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'status': 'Rebuttals updated successfully'}, status=status.HTTP_200_OK)
        else:

            print("request.data", request.data)
            paper_id = request.data.get('paper_id')
            reviewer_id = request.data.get('reviewer_id')
            score = request.data.get('score')
            confidence = request.data.get('confidence')
            comment = request.data.get('comment')

            rebuttal = request.data.get('rebuttal') 
            if rebuttal == None:
                rebuttal = ''

            # 找到对应的Review实例
            review = Review.objects.filter(paper_id=paper_id, reviewer_id=reviewer_id).first()
            if review is None:
                return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

            # 更新Review实例
            review.score = score
            review.reviewer_id = reviewer_id
            review.confidence = confidence
            review.comment = comment
            review.status = '已审稿'
            review.rebuttal = rebuttal
            review.save()

            return Response({'status': 'Review updated successfully'}, status=status.HTTP_200_OK)


# 获取当前用户的审稿记录
class MyReviewsView(APIView):
    def get(self, request):
        pc_member_id = request.query_params.get('pc_member_id')

        reviews = Review.objects.filter(reviewer_id=pc_member_id)
        paper_ids = reviews.values_list('paper_id', flat=True)
        papers = Paper.objects.filter(id__in=paper_ids).values('id', 'title', 'abstract', 'pdf', 'conference_id')

        valid_papers = []
        for paper in papers:
            # 向Conference服务请求会议的状态
            conference_response = requests.get(f'http://localhost:8002/conference/detail/?conference_id={paper["conference_id"]}')
            if conference_response.status_code != 200:
                print("请求conference状态失败:", conference_response)

            conference_data = conference_response.json()
            if conference_data['status'] == 'reviewing':
                paper_review = reviews.get(paper_id=paper['id'])

                paper_data = {
                    'conference_id': paper['conference_id'],
                    'conference_name': conference_data['full_name'],
                    'paper_id': paper['id'],
                    'title': paper['title'],
                    'abstract': paper['abstract'],
                    'pdf_url': paper['pdf'],
                    'status': '已审稿' if paper_review.score != 0 else '待审稿',
                    'rebuttal': paper_review.rebuttal,
                }

                valid_papers.append(paper_data)

        return Response(valid_papers, status=status.HTTP_200_OK)

    def post(self, request):
        # 实现下载PDF文件的逻辑

        paper_id = request.data.get('paper_id')
        paper = Paper.objects.get(id=paper_id)

        # 假设PDF文件存储在服务器上的路径
        file_path = paper.pdf

        # 确保文件存在
        if not os.path.exists(file_path):
            return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 返回文件响应
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response


class MySubmissionsView(APIView):
    def get(self, request, format=None):
        # 从查询参数中获取 username
        username = request.query_params.get('username')
        print("username", username)
        # 过滤出 submitted_by 字段匹配当前用户名的论文
        my_submissions = Paper.objects.filter(submitted_by=username)
        print("my_submissions", my_submissions)
        serializer = PaperSerializer(my_submissions, many=True)
        print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MySubmissionsView(APIView):
    def get(self, request, format=None):
        # 从查询参数中获取 username
        username = request.query_params.get('username')
        print("username", username)
        # 过滤出 submitted_by 字段匹配当前用户名的论文
        my_submissions = Paper.objects.filter(submitted_by=username)
        print("my_submissions", my_submissions)
        serializer = PaperSerializer(my_submissions, many=True)
        print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MySubmissionUpdateView(APIView):
    def get(self, request, format=None):
        # 从查询参数中获取 paper_id
        paper_id = request.query_params.get('paper_id')
        print("paper_id", paper_id)
        # 过滤出 submitted_by 字段匹配当前用户名的论文
        my_submissions = Paper.objects.filter(id=paper_id)
        print("my_submissions_update", my_submissions)
        serializer = PaperSerializer(my_submissions, many=True)
        # print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdatePaperView(APIView):
    def put(self, request, paper_id, format=None):
        try:
            paper = Paper.objects.get(id=paper_id)
        except Paper.DoesNotExist:
            return Response({'error': 'Paper not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaperSerializer(paper, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    path('update_paper/conference/<int:conference_id>/', UpdatePaperConferenceView.as_view(), name='update-paper-conference'),
class UpdatePaperConferenceView(APIView):
    def post(self, request, conference_id, format=None):
        # 使用 filter() 而不是 get()
        papers = Paper.objects.filter(conference_id=conference_id)
        
        # 如果没有找到任何论文，返回404错误
        if not papers:
            return Response({'error': 'No papers found for this conference'}, status=status.HTTP_404_NOT_FOUND)

        # 更新每篇论文的状态
        for paper in papers:
            #随机拒绝或接受论文
            if random.randint(0, 1) == 0:
                paper.status = 'rejected'
            else:
                paper.status = 'accepted'
            paper.save()

        # 将所有更新后的论文序列化并返回
        serializer = PaperSerializer(papers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class UpdateRebuttalView (APIView):
    def put(self, request, paper_id, reviewer_id ,format=None):
        try:
            review = Review.objects.get(paper_id=paper_id, reviewer_id=reviewer_id)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RebuttalView(APIView):
    def get(self, request, *args, **kwargs):
        paper_id = self.kwargs.get('paper_id')
        # print("paper_id", paper_id)
        reviews = Review.objects.filter(paper_id=paper_id)
        # print("reviews", reviews)
        serializer = ReviewSerializer(reviews, many=True)
        # print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CheckReviewsView(APIView):
    def post(self, request, conferenceId, *args, **kwargs):

        print("查找conferenceId对应的review, conferenceID:", conferenceId)
        reviews = Review.objects.filter(conference_id=conferenceId)
        for review in reviews:
            if review.status == '待审稿':
                return Response({'status': '还有未审稿的论文'}, status=status.HTTP_200_OK) 

        ### 更新会议状态
        print("更新会议状态")
        #    path('conference/detail/', ConferenceDetailView.as_view(), name='conference-detail'),
        conference_response = requests.get(f'http://localhost:8002/conference/detail/?conference_id={conferenceId}')
        if conference_response.status_code != 200:
            print("请求conference状态1失败:", conference_response)
        conference_data = conference_response.json()
        conference_data['status'] = 'reviewed'
        # 设置请求的JSON主体
        # 设置请求的JSON主体来更新会议状态
        data = {    
            'id': conferenceId,
            'status': 'rebuttal'  # 根据您的业务逻辑设置正确的状态
        }
        # 发送POST请求
        conference_response = requests.post(
            'http://localhost:8002/conference/update-status/',
            json=data
        )
        if conference_response.status_code != 200:
            print("更新conference状态失败:", conference_response)

        print("更新会议状态成功")
        return Response({'status': '所有论文都已审稿，发布成功！'}, status=status.HTTP_200_OK)