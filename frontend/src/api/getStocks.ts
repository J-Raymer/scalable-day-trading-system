import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

const API_URL = 'http://localhost:3001';
// const API_URL = import.meta.env.VITE_API_URL

const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

export interface Stock {
  stock_id: number;
  stock_name: string;
  price: number;
}


interface StockQueryResult {
  success: boolean;
  data: Stock[];
}



async function getStocks(): Promise<StockQueryResult> {
  const response = await axios.get(`${API_URL}/transaction/getStockPrices`, {
    headers,
  });
  return response.data;
}

export const useGetStocks = () => {
  return useQuery({ queryKey: ['stocks'], queryFn: getStocks });
};
