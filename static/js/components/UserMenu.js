// @flow
/* global SETTINGS:false */
import React, { Fragment } from "react"

import MixedLink from "./MixedLink"
import { routes } from "../lib/urls"

import type { User } from "../flow/authTypes"

type Props = {
  /* This is here for future use when we have custom profile avatars */
  currentUser: User,
  useScreenOverlay: boolean
}

const desktopMenuContainerProps = {
  className: "user-menu dropdown"
}

const desktopUListProps = {
  className: "dropdown-menu"
}

const overlayListItemProps = {
  className:     "authenticated-menu",
  "data-toggle": "collapse",
  "data-target": "#nav"
}

const desktopListItemProps = {
  className: "dropdown-item"
}

type MenuChildProps = {
  container?: Object,
  ul?: Object,
  li?: Object
}

const UserMenu = ({ currentUser, useScreenOverlay }: Props) => {
  /* eslint-disable prefer-const */
  let menuChildProps: MenuChildProps
  menuChildProps = useScreenOverlay
    ? {
      li: overlayListItemProps
    }
    : {
      container: desktopMenuContainerProps,
      ul:        desktopUListProps,
      li:        desktopListItemProps
    }
  return (
    <div {...menuChildProps.container || {}}>
      <div
        className="col-2 dropdown-toggle"
        id="dropdownMenuButton"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
      >
        {currentUser.name}
      </div>
      <ul {...menuChildProps.ul || {}} aria-labelledby="dropdownMenuButton">
        <li {...menuChildProps.li || {}}>
          <MixedLink dest={routes.profile.view} aria-label="Profile">
            Profile
          </MixedLink>
        </li>
        <li {...menuChildProps.li || {}}>
          <MixedLink dest={routes.dashboard} aria-label="Dashboard">
            Dashboard
          </MixedLink>
        </li>
        <li {...menuChildProps.li || {}}>
          <MixedLink dest={routes.accountSettings} aria-label="Account">
            Account
          </MixedLink>
        </li>
        <li {...menuChildProps.li || {}}>
          <MixedLink dest={routes.logout} aria-label="Sign Out">
            Sign Out
          </MixedLink>
        </li>
      </ul>
    </div>
  )
}

export default UserMenu
