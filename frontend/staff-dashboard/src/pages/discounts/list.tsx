import {
    List,
    DateField,
    ShowButton,
    Table,
    useTable,
    Space,
    EditButton,
    Tag,
    Row,
    Col,
    Card,
} from "@pankod/refine-antd";
import { CrudFilters, HttpError, useInvalidate } from "@pankod/refine-core";

import { DiscountFilterForm } from "components/discounts/filter_form";

import { IDiscount, IDiscountFilters } from "interfaces";

export const DiscountList: React.FC = () => {
    const invalidate = useInvalidate()
    const {tableQueryResult, tableProps, searchFormProps} = useTable<
        IDiscount,
        HttpError,
        IDiscountFilters
    >({
        resource: 'discounts',
        initialCurrent: 1,
        initialPageSize: 40,
        onSearch: (params) => {
            const filters: CrudFilters = [];
            const { q, redemption_type, for_flexible_pricing } = params;

            filters.push({
                field: 'q',
                operator: 'eq',
                value: q
            });

            filters.push({
                field: 'redemption_type',
                operator: 'eq',
                value: redemption_type
            });

            filters.push({
                field: 'for_flexible_pricing',
                operator: 'eq',
                value: for_flexible_pricing
            });

            return filters;
        }
    });

    const refreshList = () => {
        tableQueryResult.refetch()
    }

    return (
        <div>
            <Row gutter={[10, 10]}>
                <Col sm={24}>
                    <Card title="Find Records">
                        <DiscountFilterForm formProps={searchFormProps} />
                    </Card>
                </Col>
            </Row>

            <Row gutter={[10, 10]}>
                <Col sm={24}>
                    <List>
                        <Table {...tableProps} rowKey="id">
                            <Table.Column
                                dataIndex="discount_code"
                                title="Discount Code"
                                render={(value, record: IDiscount) => {
                                    return (<Space>{value} {record?.for_flexible_pricing ? (<Tag color="green">Financial Assistance Tier</Tag>) : null}</Space>)
                                }} />
                            <Table.Column
                                dataIndex="amount"
                                title="Amount"
                                render={(value, record: any) => parseFloat(value).toLocaleString('en-US') + ' ' + record?.discount_type }
                            />
                            <Table.Column
                                dataIndex="redemption_type"
                                title="Discount Type"
                                render={(value, record: any) => {
                                    return (<Space>{value} {record?.redemption_type !== "unlimited" && record?.is_redeemed ? (<Tag color="red">Redeemed</Tag>) : null}</Space>)
                                }}
                            />
                            <Table.Column
                                dataIndex="createdAt"
                                title="Created At"
                                render={(value) => <DateField format="LLL" value={value} />}
                            />
                            <Table.Column<IDiscount>
                                title="Actions"
                                dataIndex="actions"
                                render={(_text, record): React.ReactNode => {
                                    return (
                                        <Space>
                                            <ShowButton
                                                size="small"
                                                recordItemId={record.id}
                                                hideText
                                            />
                                            <EditButton
                                                size="small"
                                                recordItemId={record.id}
                                                hideText
                                            />
                                        </Space>
                                    );
                                }}
                            />
                        </Table>
                    </List>
                </Col>
            </Row>
        </div>
    );
};
