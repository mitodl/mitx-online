// @flow
/* global SETTINGS: false */
import React from "react"
import DocumentTitle from "react-document-title"
import { ORDER_RECEIPT_DISPLAY_PAGE_TITLE } from "../../../constants"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest } from "redux-query"

import Loader from "../../../components/Loader"
import { CartItemCard } from "../../../components/CartItemCard"
import { OrderSummaryCard } from "../../../components/OrderSummaryCard"

import { createStructuredSelector } from "reselect"
import {
  orderReceiptQuery,
  orderReceiptSelector
} from "../../../lib/queries/cart"

import type { RouterHistory } from "react-router"
import { routes } from "../../../lib/urls"
import type { Line, OrderReceipt } from "../../../flow/cartTypes"

type Props = {
  history: RouterHistory,
  orderReceipt: OrderReceipt,
  isLoading: boolean
}

export class OrderReceiptPage extends React.Component<Props> {
  renderCartItemCard(orderItem: Line) {
    return (
      <CartItemCard
        key={`itemcard_${orderItem.product.id}`}
        product={orderItem.product}
      />
    )
  }

  renderOrderSummaryCard() {
    const { orderReceipt } = this.props
    return orderReceipt ? (
      <OrderSummaryCard
        totalPrice={orderReceipt.total_price_paid}
        orderFulfilled={true}
      />
    ) : null
  }
  renderEmptyCartCard() {
    return (
      <div
        className="enrolled-item container card mb-4 rounded-0 flex-grow-1"
        key="emptycard"
      >
        <div className="row d-flex flex-sm-columm p-md-3">
          <div className="flex-grow-1 mx-3 d-sm-flex flex-column">
            <div className="detail">
              There was an error retrieving your order.
            </div>
          </div>
        </div>
      </div>
    )
  }

  render() {
    const { orderReceipt, isLoading } = this.props
    return (
      <DocumentTitle
        title={`${SETTINGS.site_name} | ${ORDER_RECEIPT_DISPLAY_PAGE_TITLE}`}
      >
        <Loader isLoading={isLoading}>
          <div className="std-page-body cart container">
            <div className="row">
              <div className="col-8 d-flex justify-content-between">
                <h1 className="flex-grow-1">Order Receipt</h1>
              </div>
              <div className="col-md-4 text-right align-middle">
                <p className="font-weight-normal mt-3">
                  <a
                    href={routes.orderHistory}
                    className="link-text align-middle"
                  >
                    Back to Order History
                  </a>
                </p>
              </div>
            </div>

            <div className="row d-flex flex-column-reverse flex-md-row">
              <div className="col-md-8 enrolled-items">
                {orderReceipt &&
                orderReceipt.lines &&
                orderReceipt.lines.length > 0
                  ? orderReceipt.lines.map(this.renderCartItemCard.bind(this))
                  : this.renderEmptyCartCard()}
              </div>
              <div className="col-md-4">{this.renderOrderSummaryCard()}</div>
            </div>
          </div>
        </Loader>
      </DocumentTitle>
    )
  }
}

const mapStateToProps = createStructuredSelector({
  orderReceipt: orderReceiptSelector,
  isLoading:    () => false
})

const mapDispatchToProps = {}

const mapPropsToConfig = () => [
  orderReceiptQuery(window.localStorage.getItem("selectedOrderReceiptId"))
]

export default compose(
  connect(
    mapStateToProps,
    mapDispatchToProps
  ),
  connectRequest(mapPropsToConfig)
)(OrderReceiptPage)
