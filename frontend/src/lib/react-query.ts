import {
  UseMutationOptions,
  DefaultOptions,
  QueryClient,
} from '@tanstack/react-query';
import '@tanstack/react-query';
// import { AxiosError } from 'axios';
//
// declare module '@tanstack/react-query' {
//   interface Register {
//     defaultError: AxiosError;
//   }
// }

export const queryConfig = {
  queries: {
    // throwOnError: true,
    refetchOnWindowFocus: false,
    retry: false,
    staleTime: 1000 * 60,
  },
} satisfies DefaultOptions;

export type ApiFnReturnType<FnType extends (...args: any) => Promise<any>> =
  Awaited<ReturnType<FnType>>;

export type QueryConfig<T extends (...args: any[]) => any> = Omit<
  ReturnType<T>,
  'queryKey' | 'queryFn'
>;

export type MutationConfig<
  MutationFnType extends (...args: any) => Promise<any>,
> = UseMutationOptions<
  ApiFnReturnType<MutationFnType>,
  Error,
  Parameters<MutationFnType>[0]
>;

export const API_URL = import.meta.env.VITE_API_URL;

export const queryClient = new QueryClient();
