// @flow
import {
  all,
  complement,
  compose,
  curry,
  defaultTo,
  either,
  find,
  isEmpty,
  isNil,
  lensPath,
  trim,
  view
} from "ramda"
import _truncate from "lodash/truncate"
import qs from "query-string"
import { assert } from "chai"
import * as R from "ramda"
import moment from "moment-timezone"

import type Moment from "moment"

import type { HttpRespErrorMessage, HttpResponse } from "../flow/httpTypes"
import type { Product } from "../flow/cartTypes"

import {
  DISCOUNT_TYPE_DOLLARS_OFF,
  DISCOUNT_TYPE_PERCENT_OFF,
  DISCOUNT_TYPE_FIXED_PRICE
} from "../constants"

/**
 * Returns a promise which resolves after a number of milliseconds have elapsed
 */
export const wait = (millis: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, millis))

/**
 * Adds on an index for each item in an iterable
 */
export function* enumerate<T>(
  iterable: Iterable<T>
): Generator<[number, T], void, void> {
  let i = 0
  for (const item of iterable) {
    yield [i, item]
    ++i
  }
}

export const isEmptyText = compose(isEmpty, trim, defaultTo(""))

export const notNil = complement(isNil)
export const firstNotNil = find(notNil)

export const goBackAndHandleEvent = curry((history, e) => {
  e.preventDefault()
  history.goBack()
})

export const preventDefaultAndInvoke = curry((invokee: Function, e: Event) => {
  if (e) {
    e.preventDefault()
  }
  invokee()
})

export const truncate = (text: ?string, length: number): string =>
  text ? _truncate(text, { length: length, separator: " " }) : ""

export const getTokenFromUrl = (props: Object): string => {
  const urlMatchPath = ["match", "params", "token"],
    querystringPath = ["location", "search"]

  let token = view(lensPath(urlMatchPath))(props)
  if (token) return token

  const querystring = view(lensPath(querystringPath))(props)
  const parsedQuerystring = qs.parse(querystring)
  token = parsedQuerystring.token
  return token || ""
}

export const makeUUID = (len: number) =>
  Array.from(window.crypto.getRandomValues(new Uint8Array(len)))
    .map(int => int.toString(16))
    .join("")
    .slice(0, len)

export const removeTrailingSlash = (str: string) =>
  str.length > 0 && str[str.length - 1] === "/"
    ? str.substr(0, str.length - 1)
    : str

export const emptyOrNil = either(isEmpty, isNil)
export const allEmptyOrNil = all(emptyOrNil)
export const anyNil = R.any(R.isNil)

export const spaceSeparated = (strings: Array<?string>): string =>
  strings.filter(str => str).join(" ")

export function* incrementer(): Generator<number, *, *> {
  let int = 1
  // eslint-disable-next-line no-constant-condition
  while (true) {
    yield int++
  }
}

export const toArray = (obj: any) =>
  Array.isArray(obj) ? obj : obj ? [obj] : undefined

export const objectToFormData = (object: Object) => {
  const formData = new FormData()

  Object.entries(object).forEach(([k, v]) => {
    if (!isNil(v)) {
      // $FlowFixMe: flow things that 'v' here can only be a Blob or File
      formData.append(k, v)
    }
  })
  return formData
}

export const assertRaises = async (
  asyncFunc: Function,
  expectedMessage: string
) => {
  let exception
  try {
    await asyncFunc()
  } catch (ex) {
    exception = ex
  }
  if (!exception) {
    throw new Error("No exception caught")
  }
  assert.equal(exception.message, expectedMessage)
}

// Example return values: "January 1, 2019", "December 31, 2019"
export const formatPrettyDate = (momentDate: Moment) =>
  momentDate.format("MMMM D, YYYY")

export const formatPrettyDateTimeAmPm = (momentDate: Moment) =>
  momentDate.format("LLL")

export const formatPrettyDateTimeAmPmTz = (monthDate: Moment) =>
  monthDate.tz(moment.tz.guess()).format("LLL z")

export const firstItem = R.view(R.lensIndex(0))

export const secondItem = R.view(R.lensIndex(1))

export const parseDateString = (dateString: ?string): ?Moment =>
  emptyOrNil(dateString) ? undefined : moment(dateString)

const getDateExtreme = R.curry(
  (compareFunc: Function, momentDates: Array<?Moment>): ?Moment => {
    const filteredDates = R.reject(R.isNil, momentDates)
    if (filteredDates.length === 0) {
      return null
    }
    return R.compose(moment, R.apply(compareFunc))(filteredDates)
  }
)

export const getMinDate = getDateExtreme(Math.min)
export const getMaxDate = getDateExtreme(Math.max)

export const newSetWith = (set: Set<*>, valueToAdd: any): Set<*> => {
  const newSet = new Set(set)
  newSet.add(valueToAdd)
  return newSet
}

export const newSetWithout = (set: Set<*>, valueToDelete: any): Set<*> => {
  const newSet = new Set(set)
  newSet.delete(valueToDelete)
  return newSet
}

export const parseIntOrUndefined = (value: any): ?number => {
  const parsed = parseInt(value)
  return isNaN(parsed) ? undefined : parsed
}

/**
 * Returns a Promise that executes a function after a given number of milliseconds then resolves
 */
export const timeoutPromise = (
  funcToExecute: Function,
  timeoutMs: number
): Promise<*> => {
  return new Promise(resolve =>
    setTimeout(() => {
      funcToExecute()
      resolve()
    }, timeoutMs)
  )
}

export const sameDayOrLater = (
  momentDate1: Moment,
  momentDate2: Moment
): boolean =>
  momentDate1.startOf("day").isSameOrAfter(momentDate2.startOf("day"))

export const isSuccessResponse = (response: HttpResponse<*>): boolean =>
  response.status >= 200 && response.status < 300

export const isErrorResponse = (response: HttpResponse<*>): boolean =>
  response.status === 0 || response.status >= 400

export const isUnauthorizedResponse = (response: HttpResponse<*>): boolean =>
  response.status === 401 || response.status === 403

export const getErrorMessages = (
  response: HttpResponse<*>
): HttpRespErrorMessage => {
  if (!response.body || !response.body.errors) {
    return null
  }
  return response.body.errors
}

export const formatLocalePrice = (amount: number | null) => {
  if (amount === null || amount < 0) amount = 0

  return amount.toLocaleString("en-US", { style: "currency", currency: "USD" })
}

export const getFlexiblePriceForProduct = (product: Product) => {
  const flexDiscountAmount =
    product && product.product_flexible_price
      ? product.product_flexible_price.amount
      : 0
  const flexDiscountType =
    product && product.product_flexible_price
      ? product.product_flexible_price.discount_type
      : null

  switch (flexDiscountType) {
  case DISCOUNT_TYPE_DOLLARS_OFF:
    return Number(product.price - flexDiscountAmount)
  case DISCOUNT_TYPE_PERCENT_OFF:
    return Number(product.price - (flexDiscountAmount / 100) * product.price)
  case DISCOUNT_TYPE_FIXED_PRICE:
    return Number(flexDiscountAmount)
  default:
    return Number(product.price)
  }
}
