# views.py

import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from .serializers import PaperSerializer, ReviewSerializer
from .models import Paper, Review


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
        paper_id = request.data.get('paper_id')
        reviewer_id = request.data.get('reviewer_id')
        score = request.data.get('score')
        confidence = request.data.get('confidence')
        comment = request.data.get('comment')

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
                    'status': '已审稿' if paper_review.score != 0 else '待审稿'
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
