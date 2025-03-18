from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    return HttpResponse("""
<h1>Barbershop</h1>
<p>Приветсвую путник. Ты находишься на сайте барбершопа. Здесь ты можешь записаться на стрижку, узнать цены и многое другое.</p>
""")