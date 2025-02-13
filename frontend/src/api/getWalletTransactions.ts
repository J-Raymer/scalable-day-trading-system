import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { API_URL, QueryConfig } from '@/lib/react-query.ts';


const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Bearer ${token}` } : {};

export interface WalletTxItem {
  wallet_tx_id: number;
  is_debit: boolean;
  amount: number;
  time_stamp: Date;
  stock_tx_id: number;
}

async function getWalletTransactions(): Promise<WalletTxItem[]> {
  const response = await axios.get(
    `${API_URL}/transaction/getWalletTransactions`,
    {
      headers,
    },
  );
  return response.data.data;
}

type UseWalletTransactionOptions = {
  queryConfig?: QueryConfig<typeof getWalletTransactions>;
};

export const useWalletTransactions = ({
  queryConfig,
}: UseWalletTransactionOptions = {}) => {
  return useQuery({
    queryKey: ['wallet'],
    queryFn: getWalletTransactions,
    ...queryConfig,
  });
};
