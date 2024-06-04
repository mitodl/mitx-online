// @flow
import { assert } from "chai"

import { NAME_REGEX } from "./ProfileFormFields"

describe("ProfileFormFields", () => {
  const nameRegex = new RegExp(NAME_REGEX)
  ;[
    "~",
    "!",
    "@",
    "&",
    ")",
    "(",
    "+",
    ":",
    ".",
    "?",
    "/",
    ",",
    "`",
    "-"
  ].forEach(validCharacter => {
    it("Name regex does not match when name begins with invalid character.", () => {
      const value = `${validCharacter}Name`
      assert.isFalse(nameRegex.test(value))
    })
  })
  // List of invalid characters that cannot exist anywhere in name
  ;[
    "/",
    "^",
    "$",
    "#",
    "*",
    "=",
    "[",
    "]",
    "`",
    "%",
    "_",
    ";",
    "<",
    ">",
    "{",
    "}",
    '"',
    "|"
  ].forEach(invalidCharacter => {
    it("Name regex does not match when invalid character exists in name.", () => {
      const value = `Name${invalidCharacter}`
      assert.isFalse(nameRegex.test(value))
    })
  })
  ;["", "~", "!", "@", "&", "+", ":", "'", ".", "?", ",", "-"].forEach(
    validCharacter => {
      it(`Name regex does match for valid name value: Name${validCharacter}`, () => {
        const value = `Name${validCharacter}`
        assert.isTrue(nameRegex.test(value))
      })
    }
  )
})
