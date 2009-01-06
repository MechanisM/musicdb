from django.shortcuts import render_to_response

from django_fuse import DirectoryResponse

def index(request):
    return render_to_response('index.html')

def fuse_index():
    return DirectoryResponse(['Albums', 'Classical'])
