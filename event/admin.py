from django.contrib import admin
import models

class EventTimeInline(admin.StackedInline):
    model = models.EventTime
    extra = 3


class EventAdmin(admin.ModelAdmin):
    inlines = [EventTimeInline]

admin.site.register(models.Event, EventAdmin)


