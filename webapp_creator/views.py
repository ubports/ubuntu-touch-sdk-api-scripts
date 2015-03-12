from django.shortcuts import render_to_response
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.template import RequestContext
from django import forms
import woc

APP_OPTIONS = (
    ('--enable-addressbar', 'Header'),
    ('--enable-back-forward', 'Back and forward buttons'),
    ('--fullscreen', 'Fullscreen'),
)


class WebappForm(forms.Form):
    displayname = forms.CharField(
        max_length=200, required=True, label='App name')
    url = forms.URLField(
        max_length=200, required=True, label='Web app URL')
    options = forms.MultipleChoiceField(
        choices=APP_OPTIONS,
        label="App options (Ctrl to multiselect)",
        required=False)
    nickname = forms.CharField(
        max_length=200, required=True, label='MyApps ID')
    fullname = forms.CharField(
        max_length=200, required=True, label='Maintainer full name')
    email = forms.EmailField(
        max_length=200, required=True, label='Maintainer email')


def webapp(request):
    webapp_form = WebappForm()
    return render_to_response(
        'webapp.html',
        {'webapp_form': webapp_form},
        context_instance=RequestContext(request))


def download(request):
    if request.method == 'POST':
        form = WebappForm(request.POST)
        tmp, click_name, click_path = woc.create(form.data)
        click_file = FileWrapper(open(click_path))
        response = HttpResponse(click_file, content_type="application/x-click")
        response['Content-Disposition'] = 'attachment; filename=%s' % (
            click_name,)
        return response
