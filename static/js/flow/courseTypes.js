import type { Product } from "./ecommerceTypes"

export type CourseDetail = {
  id: number,
  title: string,
  readable_id: string,
  feature_image_src: ?string
}

export type BaseCourseRun = {
  title: string,
  start_date: ?string,
  end_date: ?string,
  enrollment_start: ?string,
  enrollment_end: ?string,
  courseware_url: ?string,
  courseware_id: string,
  run_tag: ?string,
  products: Array<Product>,
  id: number
}

export type EnrollmentFlaggedCourseRun = BaseCourseRun & {
  expiration_date: ?string,
  is_enrolled: boolean
}

export type CourseRunDetail = BaseCourseRun & {
  course: CourseDetail
}

export type RunEnrollment = {
  run: CourseRunDetail,
  id: number,
  edx_emails_subscription: ?string
}
