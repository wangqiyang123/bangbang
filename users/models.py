from django.db import models

# Create your models here.
user_choice = (
    (0, '用户'),
    (1, '管理员'),
)


class p_User(models.Model):
    u_id = models.IntegerField(primary_key=True)

    u_name = models.CharField(max_length=10, default="未设置用户名")

    u_password = models.CharField(max_length=255)

    u_phone = models.CharField(max_length=11, unique=True)

    u_gender = models.CharField(max_length=10)

    u_birthday = models.DateField(verbose_name='生日', null=True, blank=True)

    u_email = models.CharField(max_length=30, null=True)

    u_head_picture = models.ImageField(upload_to='pics', default="pics/123.png")

    u_post = models.IntegerField(choices=user_choice, default=0)

    u_blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    sum_up_num = models.IntegerField(default=0)
    sum_down_num = models.IntegerField(default=0)

    class Meta:
        db_table = 'p_users'


class Blog(models.Model):
    nid = models.AutoField(primary_key=True)

    # 站点名称
    title = models.CharField(max_length=64,default='个人站点')

    # 副标题
    site_name = models.CharField(max_length=32,default='帮帮用户个人站点')

    theme = models.CharField(max_length=64,default='帮一帮')

    class Meta:
        db_table = 'p_blog'


class Category(models.Model):
    nid = models.AutoField(primary_key=True)

    # 分类名
    title = models.CharField(max_length=64)

    blog = models.ForeignKey(to="Blog", to_field="nid", null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'p_Category'


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)

    # 分类名
    title = models.CharField(max_length=64)

    blog = models.ForeignKey(to="Blog", to_field="nid", null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'p_Tage'


state_choice = (
    (0, '未救援'),
    (1, '已救援'),
)


class Article(models.Model):
    nid = models.AutoField(primary_key=True)

    title = models.CharField(max_length=64, verbose_name="标题")

    area = models.CharField(max_length=64)

    detail_area = models.TextField()

    upload_time = models.DateTimeField(auto_now_add=True)

    update_time = models.DateTimeField(auto_now=True)

    help_pname = models.CharField(max_length=64)

    help_pnumber = models.IntegerField()

    help_state = models.IntegerField(choices=state_choice, default=0)

    detail = models.TextField()

    blog = models.ForeignKey(to="Blog", to_field="nid", null=True, on_delete=models.CASCADE)

    category = models.ForeignKey(to="Category", to_field="nid", null=True, on_delete=models.CASCADE)

    tag = models.ManyToManyField(to="Tag", through="ArticleToTag", through_fields=('article', 'tag'))

    commit_num = models.IntegerField(default=0)
    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)



    class Meta:
        db_table = "p_article"


class ArticleToTag(models.Model):
    nid = models.AutoField(primary_key=True)

    article = models.ForeignKey(to="Article", to_field="nid", on_delete=models.CASCADE)

    tag = models.ForeignKey(to="Tag", to_field="nid", on_delete=models.CASCADE)

    class Meta:
        db_table = "p_articletotag"


class Commit(models.Model):
    nid = models.AutoField(primary_key=True)

    user = models.ForeignKey(to='p_User', to_field='u_id', on_delete=models.CASCADE)

    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)

    content = models.CharField(max_length=255)

    create_time = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(to='self', to_field='nid', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'p_Commit'


class UpAndDown(models.Model):
    nid = models.AutoField(primary_key=True)

    user = models.ForeignKey(to='p_User', to_field='u_id', on_delete=models.CASCADE)

    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)

    is_up = models.BooleanField()

    class Meta:
        unique_together = (('user', 'article'),)
        db_table = 'p_uad'
