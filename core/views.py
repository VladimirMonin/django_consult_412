from django.shortcuts import render
from django.http import HttpResponse
from .data import *

def main(request):
    return HttpResponse("""
<h1>Barbershop</h1>
<p>Приветсвую путник. Ты находишься на сайте барбершопа. Здесь ты можешь записаться на стрижку, узнать цены и многое другое.</p>
""")

def master_detail(request, master_id):
    try:
        master = [m for m in masters if m['id'] == master_id][0]
    except IndexError:
        return HttpResponse("Мастера не найдено")
    return HttpResponse(f"<h1>{master['name']}</h1>")


def thanks(request):
    masters_count = len(masters)

    context = {
        'masters_count': masters_count
    }

    return render(request, 'thanks.html', context)


def test(request):
    
    class TestClass:
        def __init__(self, name):
            self.name = name
        
        def __str__(self):
            return f'Экземпляр класса {self.__class__.__name__} с именем {self.name}'
        
        def say_my_name(self):
            return f'Меня зовут {self.name}'
    
    test_instance = TestClass('Тестовый экземпляр')
    
    context = {
        "string": "Мастер по усам",
        "number": 42,
        "list": ["Стрижка бороды", "Усы-таракан", "Укладка бровей"],
        "dict": {"best_master": "Алевтина Арбузова"},
        "class": test_instance
    }
    return render(request, 'test.html', context)