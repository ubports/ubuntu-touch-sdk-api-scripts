from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm
from django import forms
import woc

class WebappForm(forms.Form):
    displayname = forms.CharField(max_length=200)
    nickname = forms.CharField(max_length=200)
    fullname = forms.CharField(max_length=200)
    url = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=200)

def webapp(request):
    if request.method == 'POST':
        form = WebappForm(request.POST)
#        if form.is_valid():
        click_path = woc.create(form.data['url'])
        print(click_path)
    webapp_form = WebappForm()
    return render_to_response('webapp.html', { 'webapp_form': webapp_form, }, context_instance=RequestContext(request))
