import { useMutation } from '@tanstack/react-query';
import { MutationConfig } from '@/lib/react-query.ts';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

interface UseLoginProps {
  username: string;
  password: string;
}

interface LoginResult {
  token: string;
}

// Register function to handle the actual API request
async function register({
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
  mutationConfig?: MutationConfig<typeof register>;
};

export const useLogin = ({ mutationConfig }: useLoginOptions) => {
  const { onSuccess } = mutationConfig ?? {};
  return useMutation({
    mutationFn: ({ username, password }: UseLoginProps) =>
      register({ username, password }),
    onSuccess: (data, variables, context) => {
      onSuccess?.(data, variables, context);
    },
  });
};
