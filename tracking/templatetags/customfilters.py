from django import template
from django.contrib import messages
from django.forms import BoundField
from django.utils.safestring import SafeString

from tracking.models import Session

register = template.Library()


@register.filter(name="addclass")
def addclass(value: BoundField, arg: str) -> SafeString:
    return value.as_widget(attrs={"class": arg})


@register.filter(name="icon_from_word")
def icon_from_word(value: str) -> str | None:
    if c := value[0]:
        return c.upper()
    return None


@register.filter(name="message_color")
def message_color(level: int) -> str:
    if level == messages.DEBUG or level == messages.ERROR:
        return "bg-tomato-200"
    elif level == messages.SUCCESS:
        return "bg-jade-100"
    elif level == messages.INFO:
        return "bg-sky-200"
    return "bg-midaro-200"


@register.filter(name="session_utc")
def session_utc(session: Session) -> str:
    date = session.date.strftime("%Y-%m-%d")
    if session.start_time:
        time = session.start_time.strftime("%H:%M:%S")
    else:
        time = "00:00:00"
    return f"{date}T{time}Z"
