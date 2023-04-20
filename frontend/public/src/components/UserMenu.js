// @flow
import React from "react"

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
  className: "dropdown-menu dropdown-menu-end"
}

const overlayListItemProps = {
  "data-bs-target": "#nav"
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
  let dropdownIdentifier = "dropdownMenuButton"
  menuChildProps = useScreenOverlay
    ? {
      li:                 overlayListItemProps,
      dropdownIdentifier: dropdownIdentifier.concat("Mobile")
    }
    : {
      container:          desktopMenuContainerProps,
      ul:                 desktopUListProps,
      li:                 desktopListItemProps,
      dropdownIdentifier: dropdownIdentifier.concat("Desktop")
    }
  return (
    <div {...(menuChildProps.container || {})}>
      <button
        className="dropdown-toggle user-menu-button"
        id={menuChildProps.dropdownIdentifier}
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        type="button"
        role="menu"
      >
        {currentUser.name}
      </button>
      <ul
        {...(menuChildProps.ul || {})}
        aria-labelledby={menuChildProps.dropdownIdentifier}
      >
        <li {...(menuChildProps.li || {})}>
          <MixedLink dest={routes.profile} aria-label="Profile">
            Profile
          </MixedLink>
        </li>
        <li {...(menuChildProps.li || {})}>
          <MixedLink dest={routes.dashboard} aria-label="Dashboard">
            Dashboard
          </MixedLink>
        </li>
        <li {...(menuChildProps.li || {})}>
          <MixedLink dest={routes.accountSettings} aria-label="Account">
            Account
          </MixedLink>
        </li>
        <li {...(menuChildProps.li || {})}>
          <MixedLink dest={routes.orderHistory} aria-label="Order History">
            Order History
          </MixedLink>
        </li>
        <li {...(menuChildProps.li || {})}>
          <a href={routes.logout} aria-label="Sign Out">
            Sign Out
          </a>
        </li>
      </ul>
    </div>
  )
}

export default UserMenu
