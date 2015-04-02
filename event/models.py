from django.db import models
from django.utils import timezone
import pytz
import datetime

def hash(n):
    n = int(n)
    return ((0x0000FFFF & n)<<16) + ((0xFFFF0000 & n)>>16)

class EventInstance(object):
    def __init__(self, event, event_time, date):
        self.date = date.date()
        self.time = date.time()
        self.event= event
        self.event_time = event_time
        self.attending = Signup.objects.filter(event=event, date=self.date, status=Signup.ATTENDING)
        self.not_attending = Signup.objects.filter(event=event, date=self.date, status=Signup.NOT_ATTENDING)
        
    def get_date_id(self):
        return "%4d_%02d_%02d" % (self.date.year, self.date.month, self.date.day)
    
class Event(models.Model):
    name           = models.CharField(max_length=100)
    timezone       = models.CharField(max_length=50, choices=[(x,x) for x in pytz.all_timezones ], default="US/Mountain")
    description    = models.TextField()
    location_lat   = models.FloatField()
    location_lon   = models.FloatField()
    addr           = models.CharField(max_length=200)
    city           = models.CharField(max_length=100)
    state          = models.CharField(max_length=5)
    zip            = models.CharField(max_length=20)
    contact_emails = models.CharField(max_length=500, help_text='Comma separated list of email addresses')
    
    def __unicode__(self):
        return self.name

    def get_next(self):
        timezone.activate(pytz.timezone(self.timezone))
        now = timezone.now().date()
        events = [ EventInstance(self, d, d.get_next(now)) for d in self.times.all() ]
        events.sort(key=lambda x:x.date)
        return events

class EventTime(models.Model):
    DAY_CHOICES = (
        (0, "Monday",   ),
        (1, "Tuesday",  ),
        (2, "Wednesday",),
        (3, "Thursday", ),
        (4, "Friday",   ),
        (5, "Saturday", ),
        (6, "Sunday",   ),
    )

    event= models.ForeignKey(Event, related_name="times")
    day  = models.IntegerField(choices=DAY_CHOICES)
    time = models.TimeField()

    def get_next(self, now):
        dow = now.weekday()
        td = datetime.timedelta(days=(self.day - dow) % 7)
        next_date = now + td
        return datetime.datetime.combine(next_date, self.time)
    
class Signup(models.Model):
    ATTENDING     = 0
    NOT_ATTENDING = 1
    status_choices = (
        ( ATTENDING    , "I'm In",  ),
        ( NOT_ATTENDING, "I'm Out", ),
    )
    
    event = models.ForeignKey(Event, related_name="signups")
    date  = models.DateField()
    name  = models.CharField(max_length=100)
    status= models.IntegerField(choices=status_choices, blank=False, default=ATTENDING)

    def hash(self):
        return hash(self.pk)
    
class Comment(models.Model):
    class Meta:
        ordering = ["-timestamp"]
    event   = models.ForeignKey(Event, related_name="comments")
    name    = models.CharField(max_length=100)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
