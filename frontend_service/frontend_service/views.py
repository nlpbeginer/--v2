from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests


def admin(request):
    # 从 session 中获取用户信息
    user_info = request.session.get('user_info')

    # 检查用户是否为超级用户
    if not user_info['is_superuser']:
        return redirect('home')

    all_confer_response = requests.get('http://localhost:8002/conferences/')
    all_conferences = all_confer_response.json() if all_confer_response.status_code == 200 else []

    return render(request, 'admin.html', {'user_info': user_info, 'all_conferences': all_conferences})


def index(request):
    return render(request, 'main.html')


def login(request):
    return render(request, 'login.html')


def sign_up(request):
    return render(request, 'sign-up.html')


def home(request):
    # 从 session 中获取用户信息
    user_info = request.session.get('user_info')

    all_confer_response = requests.get('http://localhost:8002/conferences/')
    all_conferences = all_confer_response.json() if all_confer_response.status_code == 200 else []

    my_confer_response = requests.get('http://localhost:8002/conferences/?user_id={}'.format(user_info['id']))
    my_conferences = my_confer_response.json() if my_confer_response.status_code == 200 else []

    user_list_response = requests.get('http://localhost:8001/user_list/')
    user_list = user_list_response.json() if user_list_response.status_code == 200 else None

    # 将用户信息和用户详细信息传递给模板
    return render(request, 'dashboard.html', {
        'user_info': user_info,
        'all_conferences': all_conferences,
        'my_conferences': my_conferences,
    })

    # 将用户信息传递给模板
    # return render(request, 'dashboard.html', {'user_info': user_info, 'all_conferences': all_conferences, 'my_conferences': my_conferences})


def paper_submit(request):
    user_info = request.session.get('user_info')

    started_confer_response = requests.get('http://localhost:8002/conferences/?status={}'.format('started'))
    started_conferences = started_confer_response.json() if started_confer_response.status_code == 200 else []

    return render(request, 'paper-submit.html', {'user_info': user_info, 'started_conferences': started_conferences})


def invitation(request):
    user_info = request.session.get('user_info')

    return render(request, 'invitation.html', {'user_info': user_info})


def my_review(request):
    user_info = request.session.get('user_info')
    pc_member_id = user_info['id']

    # 向Paper服务发送请求以获取审稿数据
    response = requests.get(f'http://localhost:8003/reviews/show/?pc_member_id={pc_member_id}')
    if response.status_code == 200:
        review_info = response.json()
    else:
        review_info = []

    return render(request, 'my-review.html', {
        'user_info': user_info,
        'review_info': review_info
    })


def my_review_start_submit(request):
    if request.method == 'POST':
        user_info = request.session.get('user_info')
        conference_name = request.POST.get('conference_name')
        paper_id = request.POST.get('paper_id')
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')

        response = requests.get(f'http://localhost:8003/reviews/?paper_id={paper_id}&reviewer_id={user_info["id"]}')
        if response.status_code == 200:
            one_review = response.json()[0]
        else:
            one_review = None

        if one_review is not None:
            review_info = {
                'conference_name': conference_name,
                'paper_id': paper_id,
                'title': title,
                'abstract': abstract,
                'score': one_review['score'],
                'confidence': one_review['confidence'],
                'comment': one_review['comment'],
            }
        else:
            review_info = {
                'conference_name': conference_name,
                'paper_id': paper_id,
                'title': title,
                'abstract': abstract,
            }
        return render(request, 'my-review-submit.html', {
            'user_info': user_info,
            'review_info': review_info,
        })


def register(request):
    if request.method == 'POST':
        # 获取表单数据
        user_data = {
            'username': request.POST['signUpUsername'],
            'password': request.POST['signUpPassword'],
            'email': request.POST['signUpEmail'],
            'institution': request.POST['signUpInstitute'],
            'region': request.POST['signUpRegion'],
            'is_superuser': False,
        }

        # 向后端 API 发送请求
        response = requests.post('http://localhost:8001/register/', data=user_data)

        # 检查响应状态
        if response.status_code == 201:  # 假设 201 代表创建成功
            # 重定向到主页面
            return redirect('/login')
        else:
            # 处理错误（显示错误消息等）
            error_msg = response.text
            return render(request, 'sign-up.html', {"error_msg": error_msg})

    # 如果不是 POST 请求，显示注册表单
    return render(request, 'sign-up.html')


def login_check(request):
    if request.method == 'POST':
        user_data = {
            'username': request.POST['signInUser'],
            'password': request.POST['signInPassword']
        }

        response = requests.post('http://localhost:8001/login/', data=user_data)

        if response.status_code == 200:
            # 获取令牌
            token = response.json()['token']

            # 获取其他需要传递的数据，例如用户信息
            user_info_response = requests.get('http://localhost:8001/user_info/', headers={'Authorization': f'Token {token}'})
            user_info = user_info_response.json() if user_info_response.status_code == 200 else None

            print("是不是superuser:", user_info['is_superuser'])
            if user_info['is_superuser']:
                response = redirect('admin')
            else:
                # 设置 cookie 并重定向
                response = redirect('home')
                # response.set_cookie('token', token, httponly=True)

            # 将数据存储在 session 中，以便在主页视图中使用
            request.session['token'] = token
            request.session['user_info'] = user_info

            return response
        else:
            # 处理登录失败的情况
            error_msg = response.text
            return render(request, 'login.html', {"error_msg": error_msg})

    return render(request, 'login.html')


def logout(request):
    if 'token' in request.session:
        token = request.session['token']
        headers = {'Authorization': f'Token {token}'}

        requests.post('http://localhost:8001/logout/', headers=headers)

        # 清除 session 中的 token
        del request.session['token']

    return redirect('login')  # 重定向到登录页面


def create_conference(request):
    if request.method == 'POST':
        conference_data = {
            'acronym': request.POST['input_confer_abbre'],
            'full_name': request.POST['input_confer_full'],
            'topics': ",".join(request.POST.getlist('input_confer_topics')),  # 以逗号分隔的字符串，如 'topic1,topic2,topic3
            'held_date': request.POST['input_held_time'],
            'submission_deadline': request.POST['input_submit_ddl'],
            'review_deadline': request.POST['input_review_ddl'],
            'location': request.POST['input_held_locate'],
            'status': 'pending',
            'chair_id': request.session['user_info']['id'],
        }

        response = requests.post('http://localhost:8002/conference/create/', data=conference_data)
        if response.status_code == 201:
            return redirect('home')
        else:
            print("error：创建会议失败")
            pass

    # return render(request, 'create_conference.html')
    return redirect('home')


def approve_reject_conference(request):
    if request.method == 'POST':
        conference_id = request.POST.get('conference_id')
        action = request.POST.get('action')
        data = {
            'conference_id': conference_id,
            'action': action
        }
        # 发送 POST 请求到后端 API
        response = requests.post('http://localhost:8002/conference/approve_reject/', data=data)
        if response.status_code == 200:
            return redirect('admin')
        else:
            print("error：审批会议失败")
            pass

    # 重定向回会议列表页面（或其他适当页面）
    return redirect('admin')


def invite_pc_conference(request):
    if request.method == 'POST':
        conference_id = request.POST.get('conference_id')
        user_list_response = requests.get('http://localhost:8001/user_list/')
        user_list = user_list_response.json() if user_list_response.status_code == 200 else None
        # print("user_info", user_info)


def rebuttal(request):
    user_info = request.session.get('user_info')

    return render(request, 'rebuttal.html', {'user_info': user_info})




def my_submissions(request):
    user_info = request.session.get('user_info')

    # 向后端 API 发送请求以获取当前用户的所有投稿
    response = requests.get(f'http://localhost:8003/my_submissions/?username={user_info["username"]}')
    # print("response:", response)
    if response.status_code == 200:
        submissions = response.json()
    else:
        submissions = []

    # print("submissions:", submissions)
    return render(request, 'my-submissions.html', {
        'user_info': user_info,
        'submissions': submissions
    })

def my_submissions_rebuttal(request):
    user_info = request.session.get('user_info')

    # 向后端 API 发送请求以获取当前用户的所有review
    paper_id = request.GET.get('paper_id')
    print("正在根据paper_id查找review,paper_id号为:", paper_id)
    response = requests.get(f'http://localhost:8003/reviews/rebuttal/{paper_id}')
    print("response:", response)
    if response.status_code == 200:
        reviews = response.json()
    else:
        reviews = []

    # 判断是否有评分为 -1 或 -2 的评审
    show_rebuttal = any(review['score'] in [-1, -2] for review in reviews)

    print("reviews:", reviews)
    return render(request, 'rebuttal.html', {
        'user_info': user_info,
        'reviews': reviews,
        'show_rebuttal': show_rebuttal  # 将该变量传递到模板中
    })

def pcmember_rebuttal(request):
    user_info = request.session.get('user_info')

    # 向后端 API 发送请求以获取当前用户的所有review
    paper_id = request.GET.get('paper_id')
    print("正在根据paper_id查找review,paper_id号为:", paper_id)
    response = requests.get(f'http://localhost:8003/reviews/rebuttal/{paper_id}')
    print("response:", response)
    if response.status_code == 200:
        reviews = response.json()
    else:
        reviews = []

    # 判断是否有评分为 -1 或 -2 的评审
    show_rebuttal = any(review['score'] in [-1, -2] for review in reviews)

    print("reviews:", reviews)
    return render(request, 'pcmember_rebuttal.html', {
        'user_info': user_info,
        'reviews': reviews,
        'show_rebuttal': show_rebuttal  # 将该变量传递到模板中
    })

def my_submissions_update(request):
    user_info = request.session.get('user_info')
    # print("user_info",user_info)
    paper_id = request.GET.get('paper_id')
    # print("paper_id",paper_id)

    ###向paper service 发起请求，根据papaerid 找paper信息
    response = requests.get(f'http://localhost:8003/my_submissions/update/?paper_id={paper_id}')
    if response.status_code == 200:
        paper_info_list = response.json()
        paper_info = paper_info_list[0]
        print("paper_info",paper_info)
    else:
        paper_info = []
    
    return render(request, 'paper-submit-update.html', {'user_info': user_info, 'paper_info': paper_info})

    

