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
from django.conf.urls import url

from wagtail import views
from wagtail.coreutils import WAGTAIL_APPEND_SLASH

from cms.constants import COURSE_INDEX_SLUG, PROGRAM_INDEX_SLUG


detail_path_char_pattern = r"\w\-\.+:"

if WAGTAIL_APPEND_SLASH:
    custom_serve_pattern = (
        r"^({index_page_pattern}/(?:[{resource_pattern}]+/)*)$".format(
            index_page_pattern=COURSE_INDEX_SLUG,
            resource_pattern=detail_path_char_pattern,
        )
    )

    program_custom_serve_pattern = (
        r"^({index_page_pattern}/(?:[{resource_pattern}]+/)*)$".format(
            index_page_pattern=PROGRAM_INDEX_SLUG,
            resource_pattern=detail_path_char_pattern,
        )
    )
else:
    custom_serve_pattern = r"^({index_page_pattern}/[{resource_pattern}/]*)$".format(
        index_page_pattern=COURSE_INDEX_SLUG, resource_pattern=detail_path_char_pattern
    )
    program_custom_serve_pattern = (
        r"^({index_page_pattern}/[{resource_pattern}/]*)$".format(
            index_page_pattern=PROGRAM_INDEX_SLUG,
            resource_pattern=detail_path_char_pattern,
        )
    )


urlpatterns = [
    url(custom_serve_pattern, views.serve, name="wagtail_serve_custom"),
    url(program_custom_serve_pattern, views.serve, name="wagtail_serve_custom"),
]
