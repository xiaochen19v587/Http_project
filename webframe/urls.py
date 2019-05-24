from webframe.views import *

urls = [
    ('/time', show_time),
    ("/hello", say_hello),
    ('/bye', say_bye)
]
