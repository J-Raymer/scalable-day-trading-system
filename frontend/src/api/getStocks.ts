import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { QueryConfig } from '@/lib/react-query.ts';

const API_URL = import.meta.env.VITE_API_URL;
const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

export interface Stock {
  stock_id: number;
  stock_name: string;
  price: number;
}


async function getStocks(): Promise<Stock[]> {
  const response = await axios.get(`${API_URL}/transaction/getStockPrices`, {
    headers,
  });
  return response.data.data;
}

type UseGetStocksOptions = {
  queryConfig?: QueryConfig<typeof getStocks>;
};

export const useGetStocks = ({ queryConfig }: UseGetStocksOptions = {}) => {
  return useQuery({ queryKey: ['stocks'], queryFn: getStocks, ...queryConfig });
};
