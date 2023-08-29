import { checkFeatureFlag } from "../lib/util"
import("../../scss/layout.scss")

if (checkFeatureFlag("mitxonline-new-featured-carousel")) {
  import("../../scss/home-page/featured-product-cards.scss")
}

if (checkFeatureFlag("mitxonline-new-featured-hero")) {
  import("../../scss/home-page/home-page-hero.scss")
}

if (checkFeatureFlag("mitxonline-new-home-page-video-component")) {
  import("../../scss/home-page/home-page-video-component.scss")
}

if (checkFeatureFlag("mitxonline-new-product-page")) {
  import("../../scss/meta-product-page.scss")
}

if (checkFeatureFlag("mitxonline-new-home-page-contact-form")) {
  import("../../scss/home-page/home-page-contact-row.scss")
}
