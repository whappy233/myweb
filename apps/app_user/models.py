from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
import os



# 用户上传文件进行重命名并保存到用户文件夹, 
def user_directory_path(instance, filename):
    ext = os.path.splitex(filename)[-1]
    newname = uuid4().hex[:10] + ext
    if ext.lower() in [".jpg", ".png", ".gif", ".jpeg"]:
        sub_folder = "photo"
    elif ext.lower() in [".pdf", ".docx"]:
        sub_folder = "document"
    else:
        sub_folder = 'file'
    return os.path.join('users', str(instance.user.id), sub_folder, newname)


# UserProfile只是对User模型的扩展, 与User是1对1的关系
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # photo.url  # 获取头像URL地址
    photo = models.ImageField('头像', upload_to=user_directory_path, blank=True, default="default.png")
    telephone = models.CharField('手机号', max_length=50, blank=True, null=True)
    introduction = models.TextField('个人简介', blank=True, null=True)
    mod_date = models.DateTimeField('修改日期', auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        constraints = [ #  添加约束
            models.UniqueConstraint(fields=['telephone'], name='unique_phone'),  # 唯一约束
            # 条件约束确保一个模型实例只有满足一定的规则条件后才被创建，不满足条件的数据不会存入到数据库。
            # 下例增加了一个对员工年龄的约束，只有大于18岁的才能注册
            # models.CheckConstraint(check=models.Q(age__gte=18), name='age_gte_18')
        ]

    def __str__(self):
        return self.user.username

    @property
    def img_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url



