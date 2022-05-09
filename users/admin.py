from django.contrib import admin

# Register your models here.
from users import models

admin.site.register(models.Tag)
admin.site.register(models.Blog)
admin.site.register(models.p_User)
admin.site.register(models.Article)
admin.site.register(models.ArticleToTag)
admin.site.register(models.Category)
admin.site.register(models.Commit)
admin.site.register(models.UpAndDown)
