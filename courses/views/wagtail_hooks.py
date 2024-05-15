"""Wagtail hooks for courses app"""

from wagtail import hooks

from courses.views.wagtail_views import CourseTopicViewSet


@hooks.register("register_admin_viewset")
def register_viewset():
    """
    Register `CourseTopicViewSet` in wagtail
    """
    return CourseTopicViewSet("topics")
