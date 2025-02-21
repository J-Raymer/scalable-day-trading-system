import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { API_URL, QueryConfig } from '@/lib/react-query.ts';

const token = localStorage.getItem('token');
const headers = token ? { token } : {};

export interface PortfolioItem {
  stock_id: number;
  stock_name: string;
  quantity_owned: number;
}

async function getStockPortfolio(): Promise<PortfolioItem[]> {
  const response = await axios.get(`${API_URL}/transaction/getStockPortfolio`, {
    headers,
  });
  return response.data.data;
}

type UseStockPortfolioOptions = {
  queryConfig?: QueryConfig<typeof getStockPortfolio>;
};

export const useStockPortfolio = ({
  queryConfig,
}: UseStockPortfolioOptions = {}) => {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: getStockPortfolio,
    ...queryConfig,
  });
};
