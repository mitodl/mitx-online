"""
Upgrades legacy users in the enrollment.
This is for learners that have paid for a course and are enrolled in an upcoming
course run with a remaining exam attempt.
The list is generated outside this
command and is passed to it as a CSV file. The format of the file is:
```
learner email,courserun readable id
```
"""
from django.core.management import BaseCommand
import csv

from courses.api import create_run_enrollments
from courses.models import CourseRun, CourseRunEnrollment
from ecommerce.models import Discount, DiscountProduct, UserDiscount
from ecommerce.constants import REDEMPTION_TYPE_ONE_TIME, DISCOUNT_TYPE_PERCENT_OFF
from openedx.constants import EDX_ENROLLMENT_VERIFIED_MODE, EDX_ENROLLMENT_AUDIT_MODE
from users.models import User


class Command(BaseCommand):
    """
    Upgrade enrollment for legacy paid learners
    """

    help = "Upgrade enrollment for legacy paid learners"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "input_file",
            type=str,
            help="Input file. See documentation for file format.",
        )

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument

        with open(kwargs["input_file"], newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar="\\")

            for row in reader:
                user = User.objects.filter(email=row[0]).first()

                if user is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Can't find account for user {row[0]}, skipping row"
                        )
                    )
                    continue

                course_run = CourseRun.objects.filter(courseware_id=row[1]).first()

                if course_run is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Can't find courserun for {row[1]}, skipping row"
                        )
                    )
                    continue
                upgrade_count = 0
                enrollment = CourseRunEnrollment.objects.filter(
                    user=user, run=course_run
                ).first()
                if enrollment is None:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Can't find enrollment for user {row[0]}, course run {row[1]} skipping row"
                        )
                    )
                    continue
                if enrollment.enrollment_mode == EDX_ENROLLMENT_VERIFIED_MODE:
                    self.stdout.write(
                        self.style.ERROR(
                            f"User {user} has already verified enrollment."
                        )
                    )
                elif enrollment.enrollment_mode == EDX_ENROLLMENT_AUDIT_MODE:
                    (
                        successful_enrollments,
                        edx_request_success,
                    ) = create_run_enrollments(
                        user, [course_run], mode=EDX_ENROLLMENT_VERIFIED_MODE
                    )
                    if edx_request_success is False:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Enrollment for user {user} has failed."
                            )
                        )
                        continue
                    upgrade_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"User {user} was upgraded for {course_run.courseware_id}, edx request {edx_request_success}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f"Upgraded {upgrade_count} learners."))
