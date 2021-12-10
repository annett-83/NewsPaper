from django import template

register = template.Library()
@register.filter(name='multiply')
def multiply(value, arg):
    if isinstance(value, str) and isinstance(arg, int):
        return str(value) * arg
    else:
        raise ValueError

#Теперь каждый раз, когда мы захотим пользоваться нашими фильтрами,
#в шаблоне нужно будет прописывать следующий тег: {% load custom_filters %}.