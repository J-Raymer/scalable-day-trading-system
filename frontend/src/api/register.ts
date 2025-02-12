import { useMutation } from '@tanstack/react-query';
import { MutationConfig } from '@/lib/react-query.ts';
import axios from 'axios';

interface UseRegisterProps {
  username: string;
  password: string;
  name: string;
}

// Register function to handle the actual API request
async function register(username: string, name: string, password: string) {
  const response = await axios.post(
    'http://localhost:3001/authentication/register',
    {
      user_name: username,
      name,
      password,
    },
  );
  return response.data;
}

type UseRegisterOptions = {
  mutationConfig?: MutationConfig<typeof updateProfile>;
};

export const useRegister = ({ mutationConfig }: UseRegisterOptions) => {
  const { onSuccess } = mutationConfig ?? {};
  return useMutation({
    mutationFn: ({ username, password, name }: UseRegisterProps) =>
      register(username, name, password),
    onSuccess: (data, variables, context) => {
      // Access mutationConfig from variables and call onSuccess if defined
      onSuccess?.(data, variables, context);
    },
  });
};
