from django.shortcuts import render

from django_fuse import DirectoryResponse

def index(request):
    return render(request, 'index.html')

def fuse_index():
    return DirectoryResponse(['Albums', 'Classical'])
