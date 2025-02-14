import axios from 'axios';
import { useMutation } from '@tanstack/react-query';
import { API_URL, MutationConfig, queryClient } from '@/lib/react-query';
import { OrderType } from '@/lib/enums';

interface UseBuyStockProps {
  stockId: number;
  isBuy: boolean;
  orderType: OrderType;
  quantity: number;
  price: number;
}

const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

async function buyStock({
  stockId,
  isBuy,
  orderType,
  quantity,
  price,
}: UseBuyStockProps): Promise<void> {
  const response = await axios.post(
    `${API_URL}/engine/placeStockOrder`,
    {
      stock_id: stockId,
      is_buy: isBuy,
      order_type: orderType,
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
  mutationConfig?: MutationConfig<typeof buyStock>;
};

// TODO: When do we add wallet transactions? Is that on buy stock? Determine for invalidation
export const useBuyStock = ({ mutationConfig }: UseBuyStockOptions) => {
  const { onSuccess, ...restConfig } = mutationConfig ?? {};
  return useMutation({
    mutationFn: buyStock,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries(['portfolio', 'wallet_tx']);
      onSuccess?.(data, variables, context);
    },
    ...restConfig,
  });
};
