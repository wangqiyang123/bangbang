from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

import smtplib

from os import environ

from platform import system, node
from time import strftime
from email.mime.text import MIMEText
from email.utils import formataddr
from random import randint


from users import models
from users.models import p_User, Article

title = '这是标题（请自行更改）'
my_sender = 'bangyibang@126.com'  # 发件者邮箱（请自行更改）
my_pass = 'CDJHIIBETCTTXRZV'  # 授权码（请自行更改）
dt = strftime('%Y-%m-%d %H:%M:%S')
username = environ['USER']
system = system()
computer = node()
number = randint(100000, 999999)  # 验证码
err = Exception


def search(request, *args, **kwargs):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)

    search_word = request.GET.get('wd', '').strip()

    condition = None

    for word in search_word.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)

    search_article = []
    if condition is not None:
        search_article = models.Article.objects.filter(condition)

    number = int(request.GET.get('number', 1))
    paginator = Paginator(object_list=search_article, per_page=10)
    page_article = paginator.get_page(number)
    count = search_article.count()
    return render(request, 'search.html', locals())


def mail(request):
    global err
    ret = True
    print('嵌套入检查语句')
    try:
        my_user = request.POST.get("email")
        msg = MIMEText('验证码：' + str(number), 'plain', 'utf-8')
        msg['From'] = formataddr(["发件人名称（请自行更改）", my_sender])
        msg['To'] = formataddr(["FK", my_user])
        msg['Subject'] = "xxx的验证码（请自行更改）"
        print('已经设置好邮件信息')

        server = smtplib.SMTP_SSL("smtp.126.com", 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, [my_user, ], msg.as_string())
        server.quit()

        return HttpResponse("ok");

    except Exception as e:
        ret = False
        err = str(e)
        print('进入错误语句\n错误是%s' % (err))
    return ret


def handle_login(request):
    u_id = request.POST.get("u_id")
    password = request.POST.get("password")
    u_type = request.POST.get("post")
    u_type = int(u_type)
    rem = request.POST.get('rember')

    result = p_User.objects.filter(u_id=u_id, u_password=password)
    if result:
        request.session["is_login"] = True
        request.session["username"] = p_User.objects.get(u_id=u_id).u_name
        request.session["u_id"] = u_id
        resp = redirect(reverse("home"))

        user = models.p_User.objects.filter(u_id=u_id).first()

        post = int(user.u_post)
        print(post)

        if u_type == 1 and post == 0:
            error_msg = '您不是管理员'
            return render(request, 'login.html', {'error_msg': error_msg})

        if rem:
            # 存储cookie
            resp.set_cookie('u_id', u_id, max_age=3600 * 24 * 7)
            resp.set_cookie('password', password, max_age=3600 * 24 * 7)

        if u_type == 0:
            return redirect(reverse("home"))
        if u_type == 1:
            return redirect(reverse("admin_home"))

    else:
        error_msg = '用户名或密码错误'
        return render(request, 'login.html', {'error_msg': error_msg})


def control_reg(request):
    while True:
        user_id = randint(1000000, 9999999)
        test_user = p_User.objects.filter(u_id=user_id)
        if test_user.count() == 0:
            break

    u_name = request.POST.get("username")

    u_pwd = request.POST.get("password")

    u_mail = request.POST.get("email")

    u_tel = request.POST.get("tel")

    u_gender = request.POST.get("gender")

    u_birth = request.POST.get("birthday")

    u_check = request.POST.get("checkcode")


    if int(u_check) == number:
        blog = models.Blog.objects.create()
        p_User.objects.create(u_id=user_id, u_name=u_name, u_password=u_pwd, u_phone=u_tel, u_gender=u_gender,
                              u_birthday=u_birth, u_email=u_mail, u_blog=blog)
        return render(request, "jump.html", {'data': user_id})
    else:
        return render(request,"register.html",{'msg':"验证码错误"})

    return redirect(reverse("login"))


def jump(request):
    return redirect(reverse('jump'))


def index(request):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)

    article_list = models.Article.objects.all()

    num = 0
    id = 0

    for article in article_list:

        if article.up_num >= num:
            num = article.up_num
            id = article.pk

    best_article = models.Article.objects.get(nid=id)

    second = 0
    sid = 0
    for article in article_list:

        if article.up_num >= second and article.up_num < num:
            second = article.up_num
            sid = article.pk

    second_article = models.Article.objects.get(nid=sid)

    return render(request, "index.html", locals())


def about(request):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)
    return render(request, "about.html", locals())


def register(request):

    return render(request, "register.html")


def login(request):
    u_id = request.COOKIES.get("u_id")
    password = request.COOKIES.get("password")
    result = p_User.objects.filter(u_id=u_id, u_password=password)
    if result:
        request.session['is_login'] = True
        return render(request, "index.html")

    return render(request, "login.html")


def logout(request):
    response = HttpResponseRedirect(reverse("home"))
    response.delete_cookie('u_id')
    response.delete_cookie('password')
    request.session.flush()
    return response

# 公约界面

def single(request):
    is_login = request.session.get("is_login", None)
    return render(request, "single.html", locals())


def help(request, *args, **kwargs):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)
    article_list = models.Article.objects.all()

    tag_list = models.Tag.objects.all()

    param = kwargs.get('param')
    condition = kwargs.get('condition')

    if condition == 'tag':
        article_list = article_list.filter(tag__title=param)
    elif condition == 'category':
        article_list = article_list.filter(category__title=param)
    elif condition == 'archive':
        year_t = param.split('-')
        article_list = article_list.filter(upload_time__year=year_t[0], upload_time__month=year_t[1]).order_by("nid")

    # 所有标签对应的文章数 利用分组函数
    tag_ret = models.Tag.objects.all().annotate(count=Count('article__nid')).values_list('title', 'count')
    # 所有分类对应的文章数
    category_ret = models.Category.objects.all().values('title').annotate(count=Count('article__nid')).values_list(
        'title', 'count')
    print(param)
    # 某年某月对应的文章数
    time_ret = models.Article.objects.all().annotate(month=TruncMonth('upload_time')).values('month').annotate(
        count=Count('nid')).values_list('month', 'count')

    number = int(request.GET.get('number', 1))

    paginator = Paginator(object_list=article_list, per_page=10)

    if number not in paginator.page_range:
        number = 1

    page_article = paginator.page(number)
    return render(request, "forum.html", locals())


def blog_page(request, u_id, *args, **kwargs):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)
    user = models.p_User.objects.filter(u_id=u_id).first()
    if not user:
        return render(request, "404.html")

    # 根据用户找到个人站点
    blog = user.u_blog

    # 取到当前站点所有文章
    article_list = blog.article_set.all()

    number = int(request.GET.get('number', 1))

    # 过滤
    condition = kwargs.get('condition')
    param = kwargs.get('param')

    if condition == 'tag':
        article_list = article_list.filter(tag=param)
    elif condition == 'category':
        article_list = article_list.filter(category_id=param)
    elif condition == 'archive':
        year_t = param.split('-')
        article_list = article_list.filter(upload_time__year=year_t[0], upload_time__month=year_t[1])

    # 所有标签对应的文章数 利用分组函数
    tag_ret = models.Tag.objects.all().filter(blog=blog).annotate(count=Count('article__nid')).values_list('title',
                                                                                                           'count',
                                                                                                           'nid')
    # 所有分类对应的文章数
    category_ret = models.Category.objects.all().filter(blog=blog).annotate(count=Count('article__nid')).values_list(
        'title', 'count', 'nid')
    print(category_ret)
    # 某年某月对应的文章数
    time_ret = models.Article.objects.all().filter(blog=blog).annotate(month=TruncMonth('upload_time')).values(
        'month').annotate(
        count=Count('nid')).values_list('month', 'count')

    paginator = Paginator(object_list=article_list, per_page=10)

    if number not in paginator.page_range:
        number = 1

    page_article = paginator.page(number)

    # locals 所有变量都传过去
    return render(request, 'blog.html', locals())


def article_detail(request, u_id, pk):
    username = request.session.get("username", None)
    is_login = request.session.get("is_login", None)
    u_id = request.session.get('u_id', None)
    user = models.p_User.objects.filter(u_id=u_id).first()
    if not user:
        return render(request, "forum.html", {'msg': '登录后方可查看详情'})

    # 根据用户找到个人站点
    blog = user.u_blog

    tag_ret = models.Tag.objects.all().filter(blog=blog).annotate(count=Count('article__nid')).values_list('title',
                                                                                                           'count',
                                                                                                           'nid')
    # 所有分类对应的文章数
    category_ret = models.Category.objects.all().filter(blog=blog).annotate(count=Count('article__nid')).values_list(
        'title', 'count', 'nid')
    print(category_ret)
    # 某年某月对应的文章数
    time_ret = models.Article.objects.all().annotate(month=TruncMonth('upload_time')).values('month').annotate(
        count=Count('nid')).values_list('month', 'count')

    article = models.Article.objects.filter(pk=pk).first()
    commit_list = article.commit_set.all()
    tag_value = article.tag.all().values_list('title')

    return render(request, 'article.html', locals())


import json


def diggit(request):
    response = {'code': 100, 'msg': None}

    is_log = request.session.get('is_login')

    if is_log is not None:

        user_id = request.session.get('u_id')

        is_up = request.POST.get('is_up')

        is_up = json.loads(is_up)

        article_id = request.POST.get('article_id')

        up_ret = models.UpAndDown.objects.filter(user=user_id, article=article_id).first()

        if up_ret:
            response['code'] = 102
            response['msg'] = '您已经点过了'
        else:
            models.UpAndDown.objects.create(article_id=article_id, user_id=user_id, is_up=is_up)

            with transaction.atomic():

                if is_up:

                    models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                    response['msg'] = '点赞成功'
                else:
                    models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                    response['msg'] = '点踩成功'


    else:
        response['code'] = 101
        response['msg'] = '请先登录'

    return JsonResponse(response, safe=False)


def commit(request):
    response = {'code': 100, 'msg': None}

    is_log = request.session.get('is_login')

    if is_log is not None:

        user_id = request.session.get('u_id')

        article_id = request.POST.get('article_id')

        content = request.POST.get('content')

        parent_id = request.POST.get('parent_id')

        with transaction.atomic():

            user = p_User.objects.get(u_id=user_id)
            article = Article.objects.get(nid=article_id)
            ret = models.Commit.objects.create(article=article, content=content, user=user, parent_id=parent_id)
            models.Article.objects.filter(pk=article_id).update(commit_num=F('commit_num') + 1)

            response['username'] = ret.user.u_name
            response['reply_content'] = ret.content

            if parent_id:
                response['parent_name'] = ret.parent.user.u_name

            response['msg'] = '评论成功'


    else:
        response['code'] = 101
        response['msg'] = '请先登录'

    return JsonResponse(response, safe=False)


def home_backend(request):
    is_log = request.session.get('is_login')

    if is_log is not None:
        # 查询所有文章

        u_id = request.session.get('u_id')

        user = models.p_User.objects.get(u_id=u_id)

        article_list = models.Article.objects.filter(blog=user.u_blog)

        number = int(request.GET.get('number', 1))

        paginator = Paginator(object_list=article_list, per_page=10)

        if number not in paginator.page_range:
            number = 1

        page_article = paginator.page(number)

        return render(request, 'backend/home_backend.html', locals())

    return redirect(reverse("login"))


def add_article(request):
    is_log = request.session.get('is_login')
    if is_log is not None:
        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        return render(request, 'backend/add_article.html', locals())
    return redirect(reverse("login"))


def handle_add(request):
    is_log = request.session.get('is_login')
    if is_log is not None:

        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)

        if user.u_blog is None:
            newBlog =  models.Blog.objects.create()
            user.u_blog = newBlog
        blog = user.u_blog

        # 查询所有文章
        if request.method == 'GET':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值
            title = request.POST.get('title')

            area = request.POST.get('cityarea')
            print(area)

            detail_area = request.POST.get('detail_area')
            help_pname = request.POST.get('help_pname')
            help_pnumber = request.POST.get('help_pnumber')
            help_state = request.POST.get('help_state')
            detail = request.POST.get('detail')

            category = request.POST.get('category')

            tag_values = request.POST.get('tag_values')

            tag_values = tag_values.split(',')

            cate = models.Category.objects.filter(blog=blog, title=category)

            if cate.exists():
                cate = models.Category.objects.filter(blog=blog, title=category).first()
                a = models.Article.objects.create(title=title, area=area, detail_area=detail_area,
                                                  help_pname=help_pname,
                                                  help_state=help_state, help_pnumber=help_pnumber, detail=detail,
                                                  category=cate,
                                                  blog=user.u_blog)
            else:
                cate = models.Category.objects.create(blog=blog, title=category)
                a = models.Article.objects.create(title=title, area=area, detail_area=detail_area,
                                                  help_pname=help_pname,
                                                  help_state=help_state, help_pnumber=help_pnumber, detail=detail,
                                                  category=cate,
                                                  blog=user.u_blog)

            for tag in tag_values:
                tagg = models.Tag.objects.filter(blog=blog, title=tag).first()
                if tagg is not None:
                    models.ArticleToTag.objects.create(tag=tagg, article=a)
                else:
                    tagg = models.Tag.objects.create(blog=blog, title=tag)
                    models.ArticleToTag.objects.create(tag=tagg, article=a)

            return redirect(reverse('home_backend'))
    return redirect(reverse("login"))


def delete_artilce(request):
    is_log = request.session.get('is_login')

    if is_log is not None:
        # 查询所有文章
        if request.method == 'POST':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值

            nid = request.GET.get('nid')
            d = models.Article.objects.get(nid=nid)
            d.delete()
            return redirect(reverse('home_backend'))

    return redirect(reverse("login"))


def update_artilce(request):
    is_log = request.session.get('is_login')

    if is_log is not None:
        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        # 查询所有文章
        if request.method == 'POST':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值
            nid = request.GET.get('nid')
            article = models.Article.objects.get(nid=nid)
            blog = user.u_blog
            return render(request, 'backend/update_article.html', locals())

    return redirect(reverse("login"))


def handle_update_article(request):
    is_log = request.session.get('is_login')
    if is_log is not None:

        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        blog = user.u_blog
        # 查询所有文章
        if request.method == 'GET':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值
            title = request.POST.get('title')

            area = request.POST.get('cityarea')
            detail_area = request.POST.get('detail_area')
            help_pname = request.POST.get('help_pname')
            help_pnumber = request.POST.get('help_pnumber')
            help_state = request.POST.get('help_state')
            detail = request.POST.get('detail')
            nid = request.POST.get('nid')

            category_title = request.POST.get('category')

            artilce = models.Article.objects.get(nid=nid)

            cate_blog_id = artilce.category.blog.nid
            cate_blog = artilce.category.blog

            cates = models.Category.objects.filter(title=category_title, blog__nid=cate_blog_id).first()

            if cates:
                artilce.category = cates
            else:
                ca = models.Category.objects.create(title=category_title, blog=cate_blog)
                artilce.category = ca

            artilce.title = title
            artilce.area = area
            artilce.detail_area = detail_area
            artilce.help_pname = help_pname
            artilce.help_pnumber = help_pnumber
            artilce.help_state = help_state
            artilce.detail = detail
            artilce.save()

            return redirect(reverse('home_backend'))

    return redirect(reverse("login"))


def up_dateperson(request):
    is_log = request.session.get('is_login')

    if is_log is not None:
        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)

        return render(request, 'backend/update_person.html', locals())

    return redirect(reverse("login"))


import uuid, os


def handle_update_person(request):
    is_log = request.session.get('is_login')
    if is_log is not None:

        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        # 查询所有文章
        if request.method == 'GET':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值
            u_name = request.POST.get('u_name')
            gender = request.POST.get('gender')
            u_birthday = request.POST.get('u_birthday')
            u_head_picture = request.FILES.get('u_head_picture')
            extend = os.path.splitext(u_head_picture.name)[1]
            u_head_picture.name = str(uuid.uuid4()) + extend

            user.u_name = u_name
            user.u_gender = gender
            user.u_birthday = u_birthday
            user.u_head_picture = u_head_picture
            user.save()

            return redirect(reverse('home_backend'))

    return redirect(reverse("login"))


def update_password(request):
    is_log = request.session.get('is_login')

    if is_log is not None:
        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)

        return render(request, 'backend/update_password.html', locals())

    return redirect(reverse("login"))


def handle_password(request):
    is_log = request.session.get('is_login')
    if is_log is not None:

        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        # 查询所有文章
        if request.method == 'GET':
            return render(request, 'backend/add_article.html')
        else:
            # 根据name取值
            oldpassword = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            checkpassword = request.POST.get('checkpassword')
            print(newpassword, checkpassword)

            if oldpassword != user.u_password:
                return render(request, 'backend/update_password.html', {'old': '密码错误'})
            if oldpassword == newpassword:
                return render(request, 'backend/update_password.html', {'old': '旧密码与新密码相同'})
            if newpassword != checkpassword:
                return render(request, 'backend/update_password.html', {'msg': '两次密码输入不一致'})
            else:
                user.u_password = checkpassword
                user.save()
                response = HttpResponseRedirect(reverse("login"))
                response.delete_cookie('u_id')
                response.delete_cookie('password')
                request.session.flush()
                return response

    return redirect(reverse("login"))


def handle_administrator(request):
    is_log = request.session.get('is_login')
    if is_log is not None:

        u_id = request.session.get('u_id')
        user = models.p_User.objects.get(u_id=u_id)
        # 查询所有文章

        article_list = models.Article.objects.filter(blog=user.u_blog)
        up_sum = 0
        down_sum = 0
        for article in article_list:
            up_sum += article.up_num
            down_sum += article.down_num

        number = int(request.GET.get('number', 1))

        paginator = Paginator(object_list=article_list, per_page=10)

        if number not in paginator.page_range:
            number = 1

        page_article = paginator.page(number)

        if up_sum >= 50 and down_sum <= 5:
            user.u_post == 1
            user.sum_up_num = up_sum
            user.sum_down_num = down_sum
            user.save()

            msg = '您已升级为管理员，登录时可选择'
            return render(request, 'backend/home_backend.html', locals())
        else:
            user.sum_up_num = up_sum
            user.sum_down_num = down_sum
            user.save()
            msg = '您未拥有资格，详情请查看网站公约'
            return render(request, 'backend/home_backend.html', locals())

    return redirect(reverse("login"))


def admin_home(request):
    u_id = request.session.get('u_id')

    user = models.p_User.objects.get(u_id=u_id)

    artilce_list = models.Article.objects.all()

    dataList = [
        {'name': "南海诸岛", 'value': 0},
        {'name': '北京', 'value': 0},
        {'name': '天津', 'value': 0},
        {'name': '上海', 'value': 0},
        {'name': '重庆', 'value': 0},
        {'name': '河北', 'value': 0},
        {'name': '河南', 'value': 0},
        {'name': '云南', 'value': 0},
        {'name': '辽宁', 'value': 0},
        {'name': '黑龙江', 'value': 0},
        {'name': '湖南', 'value': 0},
        {'name': '安徽', 'value': 0},
        {'name': '山东', 'value': 0},
        {'name': '新疆', 'value': 0},
        {'name': '江苏', 'value': 0},
        {'name': '浙江', 'value': 0},
        {'name': '江西', 'value': 0},
        {'name': '湖北', 'value': 0},
        {'name': '广西', 'value': 0},
        {'name': '甘肃', 'value': 0},
        {'name': '山西', 'value': 0},
        {'name': '内蒙古', 'value': 0},
        {'name': '陕西', 'value': 0},
        {'name': '吉林', 'value': 0},
        {'name': '福建', 'value': 0},
        {'name': '贵州', 'value': 0},
        {'name': '广东', 'value': 0},
        {'name': '青海', 'value': 0},
        {'name': '西藏', 'value': 0},
        {'name': '四川', 'value': 0},
        {'name': '宁夏', 'value': 0},
        {'name': '海南', 'value': 0},
        {'name': '台湾', 'value': 0},
        {'name': '香港', 'value': 0},
        {'name': '澳门', 'value': 0}
    ]


    for article in artilce_list:
        province = article.area.split('省')[0]
        for i in range(len(dataList)):
            if list(dataList[i].values())[0] ==province:
                dict = dataList[i]
                dict['value']+=1



    genders = ['male', 'female']
    gender_date = []
    for gender in genders:
        gen = models.p_User.objects.filter(u_gender=gender).count()
        genderdict = {
            'value': gen,
            'name': gender
        }
        gender_date.append(genderdict)

    cate_type = ['灾情', '疫情', '其他']
    cate_data = []
    for type in cate_type:
        art = models.Article.objects.filter(category__title=type).count()
        cate_data.append(art)
        art = 0

    commit = 0
    for a in artilce_list:
        commit += a.commit_num

    user_count = models.p_User.objects.count()
    article_count = models.Article.objects.count()

    return render(request, "adminback/index.html", locals())


def admin_table(request):
    u_id = request.session.get('u_id')
    u_id = int(u_id)
    user = models.p_User.objects.get(u_id=u_id)
    user_list = models.p_User.objects.all()
    article_list = models.Article.objects.all()

    up_sum = 0

    for u in user_list:
        a_l = models.Article.objects.filter(blog=u.u_blog)
        for a in a_l:
            up_sum += a.up_num
        u.sum_up_num = up_sum
        up_sum = 0
        u.save()

    return render(request, "adminback/tables.html", locals())


def admin_user_delete(request):
    nid = request.GET.get('nid')
    d = models.Article.objects.get(nid=nid)
    d.delete()
    return redirect(reverse('admin_table'))


def admin_article_delete(request):
    nid = request.GET.get('nid')
    d = models.Article.objects.get(nid=nid)
    d.delete()
    return redirect(reverse('admin_table'))


def admin_editor_article(request):
    title = request.POST.get('artilce_title')
    category_title = request.POST.get('category')
    help_state = request.POST.get('help_state')
    nid = request.POST.get('get_nid')

    article = models.Article.objects.get(nid=nid)

    article.title = title
    article.help_state = help_state

    cate_blog_id = article.category.blog.nid
    cate_blog = article.category.blog

    cates = models.Category.objects.filter(title=category_title, blog__nid=cate_blog_id).first()

    if cates:
        article.category = cates
    else:
        ca = models.Category.objects.create(title=category_title, blog=cate_blog)
        article.category = ca

    article.save()
    return redirect(reverse('admin_table'))


def admin_editor_user(request):
    u_id = request.POST.get('get_id')
    post = request.POST.get('user_post')
    post = int(post)
    name = request.POST.get('user_name')
    user = models.p_User.objects.get(u_id=u_id)

    user.u_post = post
    user.u_name = name
    user.save()
    return redirect(reverse('admin_table'))
