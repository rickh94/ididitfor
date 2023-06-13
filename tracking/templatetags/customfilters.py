from django import template

register = template.Library()


@register.filter(name="addclass")
def addclass(value, arg):
    return value.as_widget(attrs={"class": arg})


@register.filter(name="addclass")
def datepicker(value):
    return value.as_widget(attrs={"type": "date"})


@register.filter(name="icon_from_word")
def icon_from_word(value: str):
    if c := value[0]:
        return c.upper()
    else:
        None
