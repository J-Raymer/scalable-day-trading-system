import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { API_URL, QueryConfig } from '@/lib/react-query.ts';

const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

export interface Stock {
  stock_id: number;
  stock_name: string;
  current_price: number;
}

async function getStockPrices(): Promise<Stock[]> {
  const response = await axios.get(`${API_URL}/transaction/getStockPrices`, {
    headers,
  });
  return response.data.data;
}

type UseGetStocksOptions = {
  queryConfig?: QueryConfig<typeof getStockPrices>;
};

export const useStockPrices = ({ queryConfig }: UseGetStocksOptions = {}) => {
  return useQuery({
    queryKey: ['stocks'],
    queryFn: getStockPrices,
    ...queryConfig,
  });
};
