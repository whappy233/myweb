from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
import os


def uuid4_hex():
    return uuid4().hex[:10]


# 用户上传文件进行重命名并保存到用户文件夹,
def user_directory_path(instance, filename):
    ext = os.path.splitext(filename)[-1]
    newname = uuid4().hex[:10] + ext
    if ext.lower() in [".jpg", ".png", ".gif", ".jpeg"]:
        sub_folder = "photo"
    elif ext.lower() in [".pdf", ".docx"]:
        sub_folder = "document"
    else:
        sub_folder = 'file'
    return os.path.join('users', str(instance.uuid), sub_folder, newname)



# UserProfile只是对User模型的扩展, 与User是1对1的关系
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile',
                                blank=True, null=True,
                                verbose_name='关联的用户信息')
    # photo.url  # 获取头像URL地址
    photo = models.ImageField('头像', upload_to=user_directory_path, blank=True, null=True)
    telephone = models.CharField('手机号', max_length=50, blank=True, null=True)
    introduction = models.TextField('个人简介', blank=True, null=True)
    mod_date = models.DateTimeField('修改日期', auto_now=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    # 游民必填
    w_name = models.CharField('昵称(游民)', max_length=20, blank=True, null=True)
    w_email = models.EmailField('邮箱(游民)', max_length=50, blank=True, null=True)
    is_wanderer = models.BooleanField('是否是游民', default=False)

    uuid = models.CharField('唯一标识', max_length=10, unique=True, default=uuid4_hex, editable=False)

    class Meta:
        verbose_name = 'User Profile'
        constraints = [  # 添加约束
            models.UniqueConstraint(
                fields=['telephone'], name='unique_phone'),  # 唯一约束
            # 条件约束确保一个模型实例只有满足一定的规则条件后才被创建，不满足条件的数据不会存入到数据库。
            # 下例增加了一个对员工年龄的约束，只有大于18岁的才能注册
            # models.CheckConstraint(check=models.Q(age__gte=18), name='age_gte_18')
        ]

    def save(self, *args, **kwargs):
        if self.user:
            self.w_name = self.w_email = None
            self.is_wanderer = False
        elif self.w_name and self.w_email:
            # self._state.adding is True 为创建, 否则为更新
            if self._state.adding and UserProfile.objects.filter(w_email=self.w_email).exists():
                raise ValueError('w_email 字段要求唯一')
            else:
                self.is_wanderer = True
        else:
            raise ValueError('不允未关联User对象模型的 w_name 和 w_email 字段为空')
        super().save(*args, **kwargs)

    @property
    def username(self):
        if self.is_wanderer:
            return self.w_name
        else:
            return self.user

    @property
    def email(self):
        if self.is_wanderer:
            return self.w_email
        else:
            return self.user.email

    def __str__(self):
        return str(self.username)

    @property
    def img_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
