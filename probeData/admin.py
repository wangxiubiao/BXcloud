from django.contrib import admin
from probeData.models import SiteInfo,ParamInfo,WarningInfo,UrgentPerson

# Register your models here.
class ContactUrgentPerson(admin.ModelAdmin):
    list_display  = ('name','phone', 'email','siteId')

class ContactSiteInfo(admin.ModelAdmin):
    list_display  = ('siteName','siteLng','siteLat','state','desc')

class ContactParamInfo(admin.ModelAdmin):
    list_display = ('paramTime','paramType','data','unit','siteId')
    search_fields = ('paramType','siteId__id')

class ContactWarningInfo(admin.ModelAdmin):
    list_display = ('time','warningType','warningParam','warningValue','limitValue','siteId','isHandle')
    search_fields = ('warningType', 'warningParam','siteId__id')


admin.site.register(SiteInfo,ContactSiteInfo)
admin.site.register(ParamInfo,ContactParamInfo)
admin.site.register(WarningInfo,ContactWarningInfo)
admin.site.register(UrgentPerson,ContactUrgentPerson)