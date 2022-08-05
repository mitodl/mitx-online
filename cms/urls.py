"""
Custom URLs for serving Wagtail pages

NOTE:
These definitions are needed because we want to serve pages at URLs that match
edX course ids, and those edX course ids contain characters that do not match Wagtail's
expected URL pattern (https://github.com/wagtail/wagtail/blob/a657a75/wagtail/core/urls.py)

Example: "course-v1:edX+DemoX+Demo_Course" – Wagtail's pattern does not match the ":" or
the "+" characters.

The pattern(s) defined here serve the same Wagtail view that the library-defined pattern serves.
"""
from django.urls import re_path

from wagtail.core import views
from wagtail.core.utils import WAGTAIL_APPEND_SLASH

from cms.constants import COURSE_INDEX_SLUG, PROGRAM_INDEX_SLUG


detail_path_char_pattern = r"\w\-\.+:"

if WAGTAIL_APPEND_SLASH:
    custom_serve_pattern_course = (
        r"^({index_page_pattern}/(?:[{resource_pattern}]+/)*)$".format(
            index_page_pattern=COURSE_INDEX_SLUG,
            resource_pattern=detail_path_char_pattern,
        )
    )

    custom_serve_pattern_program = (
        r"^({index_page_pattern}/(?:[{resource_pattern}]+/)*)$".format(
            index_page_pattern=PROGRAM_INDEX_SLUG,
            resource_pattern=detail_path_char_pattern,
        )
    )
# else:
#     custom_serve_pattern_course = (
#         r"^({index_page_pattern}/[{resource_pattern}/]*)$".format(
#             index_page_pattern=COURSE_INDEX_SLUG, resource_pattern=detail_path_char_pattern
#         )
#     )

#     custom_serve_pattern_program = (
#         r"^({index_page_pattern}/[{resource_pattern}/]*)$".format(
#             index_page_pattern=PROGRAM_INDEX_SLUG, resource_pattern=detail_path_char_pattern
#         ),
#     )


urlpatterns = [
    re_path(custom_serve_pattern_course, views.serve, name="wagtail_serve_custom"),
    re_path(
        custom_serve_pattern_program, views.serve, name="wagtail_serve_custom_program"
    ),
]
