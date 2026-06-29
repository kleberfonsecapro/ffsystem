from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {"income": 0, "expense": 0})
