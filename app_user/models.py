from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
import os



# 用户上传文件进行重命名并保存到用户文件夹, 
def user_directory_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1]
    filename = f'{uuid4().hex[:10]}.{ext}'
    sub_folder = 'file'
    if ext.lower() in ["jpg", "png", "gif", "jpeg"]:
        sub_folder = "photo"
    if ext.lower() in ["pdf", "docx"]:
        sub_folder = "document"
    return os.path.join('users', str(instance.user.id), sub_folder, filename)



# Model ---------------------------------------------------
# UserProfile只是对User模型的扩展, 与User是1对1的关系
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField('头像', upload_to=user_directory_path, blank=True, default=os.path.join("users", "default.jpeg"))
    org = models.CharField('组织', max_length=128, blank=True)
    telephone = models.CharField('手机号', max_length=50, blank=True)
    mod_date = models.DateTimeField('最近修改', auto_now=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user.username

    # 验证邮箱是否验证过
    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False


    @property
    def img_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
