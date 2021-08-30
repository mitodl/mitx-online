"""Constants for the courses app"""

CONTENT_TYPE_MODEL_PROGRAM = "program"
CONTENT_TYPE_MODEL_COURSE = "course"
CONTENT_TYPE_MODEL_COURSERUN = "courserun"
DEFAULT_COURSE_IMG_PATH = "images/mit-dome.png"
VALID_PRODUCT_TYPES = {CONTENT_TYPE_MODEL_COURSERUN, CONTENT_TYPE_MODEL_PROGRAM}
VALID_PRODUCT_TYPE_CHOICES = list(zip(VALID_PRODUCT_TYPES, VALID_PRODUCT_TYPES))

PROGRAM_TEXT_ID_PREFIX = "program-"
ENROLLABLE_ITEM_ID_SEPARATOR = "+"
TEXT_ID_RUN_TAG_PATTERN = r"\{separator}(?P<run_tag>R\d+)$".format(
    separator=ENROLLABLE_ITEM_ID_SEPARATOR
)
PROGRAM_RUN_ID_PATTERN = (
    r"^(?P<text_id_base>{program_prefix}.*){run_tag_pattern}".format(
        program_prefix=PROGRAM_TEXT_ID_PREFIX, run_tag_pattern=TEXT_ID_RUN_TAG_PATTERN
    )
)

ENROLL_CHANGE_STATUS_DEFERRED = "deferred"
ENROLL_CHANGE_STATUS_TRANSFERRED = "transferred"
ENROLL_CHANGE_STATUS_REFUNDED = "refunded"
ALL_ENROLL_CHANGE_STATUSES = [
    ENROLL_CHANGE_STATUS_DEFERRED,
    ENROLL_CHANGE_STATUS_TRANSFERRED,
    ENROLL_CHANGE_STATUS_REFUNDED,
]
ENROLL_CHANGE_STATUS_CHOICES = list(
    zip(ALL_ENROLL_CHANGE_STATUSES, ALL_ENROLL_CHANGE_STATUSES)
)
