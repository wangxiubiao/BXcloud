from django.db import models

# Create your models here.

#站点信息类
class SiteInfo(models.Model):
    siteName = models.CharField(max_length=40)
    siteLat = models.CharField(max_length=20)
    siteLng = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    desc = models.CharField(max_length=200)

    def __str__(self):
        return self.siteName


#参数信息类
class ParamInfo(models.Model):
    paramTime = models.DateTimeField()
    paramType = models.CharField(max_length=20)
    data = models.FloatField()
    unit = models.CharField(max_length=20)
    siteId = models.ForeignKey('SiteInfo',on_delete=models.CASCADE)


#报警信息类
class WarningInfo(models.Model):
    time = models.DateTimeField()
    warningType = models.CharField(max_length=20)
    warningParam = models.CharField(max_length=20)
    warningValue = models.FloatField()
    limitValue = models.FloatField()
    siteId = models.ForeignKey('SiteInfo',on_delete=models.CASCADE)
    isHandle = models.BooleanField()

#应急联系人
class UrgentPerson(models.Model):
    name = models.CharField(max_length=20)
    phone = models.CharField(max_length=11)
    email = models.CharField(max_length=20)
    siteId = models.ForeignKey('SiteInfo',on_delete=models.CASCADE)


#用户信息类
class User(models.Model):
    gender = (
        ('male','男'),
        ('female','女'),
    )

    name = models.CharField(max_length=128,unique=True)
    pwd = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32,choices=gender,default='男')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"






