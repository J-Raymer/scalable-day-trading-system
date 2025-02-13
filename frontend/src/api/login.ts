import { useMutation } from '@tanstack/react-query';
import { API_URL, MutationConfig } from '@/lib/react-query.ts';
import axios from 'axios';

interface UseLoginProps {
  username: string;
  password: string;
}

interface LoginResult {
  token: string;
}

// Register function to handle the actual API request
async function login({
  username,
  password,
}: UseLoginProps): Promise<LoginResult> {
  const response = await axios.post(`${API_URL}/authentication/login`, {
    user_name: username,
    password,
  });
  return response.data.data;
}

type useLoginOptions = {
  mutationConfig?: MutationConfig<typeof login>;
};

export const useLogin = ({ mutationConfig }: useLoginOptions) => {
  const { onSuccess, ...restConfig } = mutationConfig ?? {};
  return useMutation({
    mutationFn: login,
    onSuccess: (data, variables, context) => {
      onSuccess?.(data, variables, context);
    },
    ...restConfig,
  });
};
