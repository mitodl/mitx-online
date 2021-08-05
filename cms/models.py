"""CMS model definitions"""
from django.conf import settings
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import StreamBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.models import Image
from wagtail.images.edit_handlers import ImageChooserPanel

from cms.blocks import ResourceBlock, PriceBlock


class HomePage(Page):
    """
    Site home page
    """

    template = "home_page.html"

    hero = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Main image displayed at the top of the home page. (The recommended dimensions for hero image are "
        "1920x400)",
    )
    hero_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The title text to display in the hero section of the home page.",
    )
    hero_subtitle = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The subtitle text to display in the hero section of the home page.",
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("hero"),
        FieldPanel("hero_title"),
        FieldPanel("hero_subtitle"),
    ]
    parent_page_types = [Page]
    subpage_types = [
        "CoursePage",
        "ResourcePage",
    ]


class ProductPage(Page):
    """
    Abstract detail page for course runs and any other "product" that a user can enroll in
    """

    class Meta:
        abstract = True

    description = RichTextField(
        blank=True, help_text="The description shown on the product page"
    )

    length = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="A short description indicating how long it takes to complete (e.g. '4 weeks').",
    )

    effort = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="A short description indicating how much effort is required (e.g. 1-3 hours per week).",
    )

    price = StreamField(
        StreamBlock([("price_details", PriceBlock())], max_num=1),
        blank=True,
        help_text="Specify the product price details.",
    )

    prerequisites = RichTextField(
        null=True,
        blank=True,
        help_text="A short description indicating prerequisites of this course.",
    )

    about = RichTextField(null=True, blank=True, help_text="About this course details.")

    what_you_learn = RichTextField(
        null=True, blank=True, help_text="What you will learn from this course."
    )

    feature_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that will be used where the course is featured or linked.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("length"),
        FieldPanel("effort"),
        FieldPanel("price"),
        FieldPanel("prerequisites"),
        FieldPanel("about"),
        FieldPanel("what_you_learn"),
        FieldPanel("feature_image"),
    ]
    parent_page_types = ["HomePage"]
    subpage_types = []


class CoursePage(ProductPage):
    """
    Detail page for courses
    """

    course = models.OneToOneField(
        "courses.Course", null=True, on_delete=models.SET_NULL, related_name="page"
    )

    @property
    def product(self):
        """Gets the product associated with this page"""
        return self.course

    template = "product_page.html"

    def get_context(self, request, *args, **kwargs):
        first_unexpired_run = self.product.first_unexpired_run
        return {
            **super().get_context(request, *args, **kwargs),
            "start_date": first_unexpired_run.start_date
            if first_unexpired_run
            else None,
        }

    content_panels = [FieldPanel("course")] + ProductPage.content_panels


class ResourcePage(Page):
    """
    Basic resource page class for pages containing basic information (FAQ, etc.)
    """

    template = "resource_page.html"
    parent_page_types = ["HomePage"]

    header_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload a header image that will render in the resource page. (The recommended dimensions for the image are 1920x300)",
    )

    content = StreamField(
        [("content", ResourceBlock())],
        blank=False,
        help_text="Enter details of content.",
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("header_image"),
        StreamFieldPanel("content"),
    ]

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "site_name": settings.SITE_NAME,
        }
