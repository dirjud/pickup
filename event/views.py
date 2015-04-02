from django.core.context_processors import csrf
import models
from django import shortcuts, http
import django.forms
import datetime

class SignupForm(django.forms.ModelForm):
    class Meta:
        model = models.Signup
        exclude=["date"]
        widgets = {
            "name": django.forms.TextInput(attrs={'placeholder': 'Name'}),
            }

        
    def __init__(self, event, *args, **kws):
        super(SignupForm, self).__init__(*args, **kws)
        self.dates = []
        for x in event.get_next():
            field = django.forms.BooleanField(required=False)
            name = "date_" + x.get_date_id()
            self.fields[name] = field
            self.dates.append((type(self).__getitem__(self, name),x))

    def clean(self, *args, **kws):
        cleaned_data = super(SignupForm, self).clean(*args, **kws)
        found1 = False
        for k,v in cleaned_data.items():
            if k.startswith("date_") and v:
                found1 = True
                break
        if not(found1):
            raise django.forms.ValidationError("No date selected. Select a date to signup for and try again.")
        return cleaned_data

def redirect(event):
    return http.HttpResponseRedirect("?event="+str(event.pk))

class CommentForm(django.forms.ModelForm):
    class Meta:
        model   = models.Comment
        include = [ "name", "comment" ]
        widgets = {
            "name"   : django.forms.TextInput(attrs={'placeholder'   : 'Name'}),
            "comment": django.forms.Textarea(attrs={'placeholder' : 'Comment'}),
            }

def signup(request):
    events = models.Event.objects.all().order_by("name")
    event_pk = request.GET.get("event", None)
    
    if event_pk is None:
        event = events[0]
    else:
        event = models.Event.objects.get(pk=event_pk)
        
    context = dict(
        event  = event,
        events = events,
    )
    context.update(csrf(request))

    if "del" in request.GET:
        try:
            models.Signup.objects.get(event=event, pk=models.hash(int(request.GET["del"]))).delete()
        except models.Signup.DoesNotExist:
            pass
        return redirect(event)
    
    if request.method == "POST":
        if request.POST["action"] == "signup":
            context["form"] = SignupForm(event, request.REQUEST)
            if context["form"].is_valid():
                d = context["form"].cleaned_data
                for k,v in request.POST.items():
                    if k.startswith("date") and v:
                        found1 = True
                        su = models.Signup(
                            date  = datetime.date(*([int(x) for x in k[5:].split("_")])),
                            name  = d["name"],
                            status= d["status"],
                            event = event,
                        )
                        su.save()
                return redirect(event)

        elif request.POST["action"] == "comment":
            context["comment_form"] = CommentForm(request.REQUEST)
            if context["comment_form"].is_valid():
                d = context["comment_form"].cleaned_data
                c = models.Comment(name=d["name"], comment=d["comment"], event=event)
                c.save()
                return redirect(event)
                
    context["comments"] = event.comments.all()[:10]

    if "form" not in context:
        context["form"] = SignupForm(event)

    if "comment_form" not in context:
        context["comment_form"] = CommentForm()

        
    return shortcuts.render(request, "event/signup.html", context)
