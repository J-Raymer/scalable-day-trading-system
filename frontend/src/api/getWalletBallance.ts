import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { API_URL, QueryConfig } from '@/lib/react-query.ts';

const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

export interface Wallet {
  balance: number;
}

async function getWalletBalance(): Promise<Wallet[]> {
  const response = await axios.get(`${API_URL}/transaction/getWalletBalance`, {
    headers,
  });
  return response.data.data;
}

type UseGetWalletOptions = {
  queryConfig?: QueryConfig<typeof getWalletBalance>;
};

export const useWalletBalance = ({ queryConfig }: UseGetWalletOptions = {}) => {
  return useQuery({
    queryKey: ['wallet_balance'],
    queryFn: getWalletBalance,
    ...queryConfig,
  });
};
