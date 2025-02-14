import { useMutation } from '@tanstack/react-query';
import { API_URL, MutationConfig } from '@/lib/react-query.ts';
import axios from 'axios';

interface UseUpdateWalletProps {
  amount: number;
}

async function updateWallet({ amount }: UseUpdateWalletProps): Promise<void> {
  const response = await axios.post(`${API_URL}/transaction/addMoneyToWallet`, {
    amount,
  });
  return response.data.data;
}

type UseUpdateWalletOptions = {
  mutationConfig?: MutationConfig<typeof updateWallet>;
};

export const useUpdateWallet = ({
  mutationConfig,
}: UseUpdateWalletOptions = {}) => {
  const { onSuccess, ...restConfig } = mutationConfig ?? {};
  return useMutation({
    mutationFn: updateWallet,
    onSuccess: (data, variables, context) => {
      // This is where you would do something like invalidate a query if say, updating stocks.
      onSuccess?.(data, variables, context);
    },
    ...restConfig,
  });
};
