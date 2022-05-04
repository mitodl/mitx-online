import { 
    useForm,
    Form,
    Input,
    InputNumber,
    Select,
    Edit,
 } from "@pankod/refine-antd";

import { IDiscount } from "interfaces";


export const DiscountEdit = () => {
    const { formProps, saveButtonProps, queryResult } = useForm<IDiscount>();
    const discount_type = queryResult?.data?.data.discount_type

    return (
        <div>
            <Edit saveButtonProps={saveButtonProps}>
                <Form {...formProps} layout="vertical">
                    <Form.Item label="Discount Code" name="discount_code">
                        <Input />
                    </Form.Item>
                    <Form.Item label="Redemption Type" name="redemption_type">
                        <Select options={[
                            { label: 'Unlimited', value: 'unlimited' },
                            { label: 'One-Time', value: 'one-time' },
                            { label: 'One Time Per User', value: 'one-time-per-user' }, 
                        ]}></Select>
                    </Form.Item>
                    <Form.Item label="Discount Type" name="discount_type">
                        <Select options={[
                            { label: 'Percent Off', value: 'percent-off' },
                            { label: 'Dollars Off', value: 'dollars-off' },
                            { label: 'Fixed Price', value: 'fixed-price' }, 
                        ]}></Select>
                    </Form.Item>
                    <Form.Item label="Amount" name="amount">
                        <InputNumber precision={2} />
                    </Form.Item>
                </Form>
            </Edit>
        </div>
    );
};