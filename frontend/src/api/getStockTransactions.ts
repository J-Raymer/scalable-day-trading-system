import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { API_URL, QueryConfig } from '@/lib/react-query';
import { OrderStatus, OrderType } from '@/lib/enums';

const token = localStorage.getItem('token');
const headers = token ? { token } : {};

export interface StockTransactions {
  stock_tx_id: number;
  stock_id: number;
  wallet_tx_id: number;
  order_status: OrderStatus;
  is_buy: boolean;
  order_type: OrderType;
  stock_price: number;
  quantity: number;
  parent_tx_id: number | undefined;
  time_stamp: Date;
  user_id: string;
}

async function getStockTransactions(): Promise<StockTransactions[]> {
  const response = await axios.get(
    `${API_URL}/transaction/getStockTransactions`,
    {
      headers,
    },
  );
  return response.data.data;
}

type UseGetStockTransactionsOptions = {
  queryConfig?: QueryConfig<typeof getStockTransactions>;
};

export const useStockTransactions = ({
  queryConfig,
}: UseGetStockTransactionsOptions = {}) => {
  return useQuery({
    queryKey: ['stock_tx'],
    queryFn: getStockTransactions,
    ...queryConfig,
  });
};
