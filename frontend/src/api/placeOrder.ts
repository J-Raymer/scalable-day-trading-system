import axios from 'axios';
import { useMutation } from '@tanstack/react-query';
import { API_URL, MutationConfig, queryClient } from '@/lib/react-query';
import { OrderType } from '@/lib/enums';

interface UseBuyStockProps {
  stockId: number;
  quantity: number;
  price: number;
  isBuy: boolean;
}

const token = localStorage.getItem('token');
const headers = token ? { token } : {};

async function placeOrder({
  stockId,
  quantity,
  price,
  isBuy,
}: UseBuyStockProps): Promise<void> {
  const response = await axios.post(
    `${API_URL}/engine/placeStockOrder`,
    {
      stock_id: stockId,
      is_buy: isBuy,
      order_type: isBuy ? OrderType.MARKET : OrderType.LIMIT,
      quantity,
      price,
    },
    {
      headers,
    },
  );
  return response.data.data;
}

type UseBuyStockOptions = {
  mutationConfig?: MutationConfig<typeof placeOrder>;
};

export const usePlaceOrder = ({ mutationConfig }: UseBuyStockOptions = {}) => {
  const { onSuccess, ...restConfig } = mutationConfig ?? {};
  return useMutation({
    mutationFn: placeOrder,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries(['portfolio']);
      queryClient.invalidateQueries(['wallet_tx']);
      queryClient.invalidateQueries(['stock_tx']);
      queryClient.invalidateQueries(['stocks']);
      onSuccess?.(data, variables, context);
    },
    ...restConfig,
  });
};
