import axios from 'axios';
import { useMutation } from '@tanstack/react-query';
import { API_URL, MutationConfig, queryClient } from '@/lib/react-query';

interface UseCancelOrderProps {
  stockTxId: number;
}

const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

async function cancelOrder({ stockTxId }: UseCancelOrderProps): Promise<void> {
  const response = await axios.post(
    `${API_URL}/engine/cancelStockTransaction`,
    {
      stock_tx_id: stockTxId,
    },
    {
      headers,
    },
  );
  return response.data;
}

type UseCancelOrderOptions = {
  mutationConfig?: MutationConfig<typeof cancelOrder>;
};

export const useCancelOrder = ({
  mutationConfig,
}: UseCancelOrderOptions = {}) => {
  const { onSuccess, ...restConfig } = mutationConfig ?? {};
  return useMutation({
    mutationFn: cancelOrder,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries(['stock_tx']);
      queryClient.invalidateQueries(['portfolio']);
      onSuccess?.(data, variables, context);
    },
    ...restConfig,
  });
};
