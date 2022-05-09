from django.contrib import admin

from django.urls import path, re_path

from web import views

urlpatterns = [
    path("home/", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("jump/", views.jump, name="jump"),
    path("login/", views.login, name="login"),
    path("handle_login/", views.handle_login, name="handle_login"),
    path("mail/", views.mail, name="mail"),
    path("register/", views.register, name="register"),
    path("save_register/", views.control_reg, name="con_reg"),
    # 公约
    path("gongyue/", views.single, name="single"),
    path("logout/", views.logout, name="logout"),
    path("help/", views.help, name="help"),
    path("search/",views.search,name="search"),


    # 后台管理员

    path("admin_home/",views.admin_home,name="admin_home"),
    path("admin_table/",views.admin_table,name="admin_table"),


    path("admin_editor_article/",views.admin_editor_article,name="admin_editor_article"),
    path("admin_article_delete/",views.admin_article_delete),
    path("admin_editor_user/",views.admin_editor_user,name="admin_editor_user"),
    path("admin_user_delete/",views.admin_user_delete),


    # 后台管理首页

    path("home_backend/",views.home_backend,name="home_backend"),

    # 添加文章
    path("add_article/",views.add_article,name="add_article"),
    path("handle_add/",views.handle_add,name="handle_add"),

    # 删除文章
    path("delete_artilce/",views.delete_artilce,name="delete_artilce"),

    # 升级管理员
    path("up_admin/",views.handle_administrator,name="up_admin"),

    # 编辑文章
    path("update_artilce/",views.update_artilce,name="update_artilce"),
    path("handle_update_article/",views.handle_update_article,name="handle_update_article"),


    # 修改个人信息
    path("up_dateperson/",views.up_dateperson,name="up_dateperson"),
    path("handle_update_person/",views.handle_update_person,name="handle_update_person"),

    # 修改密码
    path("update_password/",views.update_password,name="update_password"),
    path("handle_password/",views.handle_password,name="handle_password"),

    # 点赞路由
    path("diggit/",views.diggit),

    # 评论路由
    path("commit/",views.commit),

    re_path(r'^help/(?P<condition>category|tag|archive)/(?P<param>.*)/$',views.help),

    re_path(r'^(?P<u_id>\d+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.blog_page, name="blog_cate"),

    # 文章详情
    re_path(r'^(?P<u_id>\d+)/article/(?P<pk>\d+)$', views.article_detail),
    # 放最后
    re_path(r'^(?P<u_id>\d+)/$', views.blog_page, name="blog_page")
]
