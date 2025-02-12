import { useMutation } from '@tanstack/react-query';
import { MutationConfig } from '@/lib/react-query.ts';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

interface UseRegisterProps {
  username: string;
  password: string;
  name: string;
}

interface RegisterResult {
  success: boolean;
  data: { token: string };
}

// Register function to handle the actual API request
async function register({
  username,
  password,
  name,
}: UseRegisterProps): Promise<RegisterResult> {
  const response = await axios.post(`${API_URL}/authentication/register`, {
    user_name: username,
    name,
    password,
  });
  return response.data;
}

type UseRegisterOptions = {
  mutationConfig?: MutationConfig<typeof register>;
};

export const useRegister = ({ mutationConfig }: UseRegisterOptions) => {
  const { onSuccess } = mutationConfig ?? {};
  return useMutation({
    mutationFn: ({ username, password, name }: UseRegisterProps) =>
      register({ username, name, password }),
    onSuccess: (data, variables, context) => {
      onSuccess?.(data, variables, context);
    },
  });
};
