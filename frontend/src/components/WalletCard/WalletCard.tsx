import React from 'react';
import './WalletCard.scss';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { useWalletBalance } from '@/api/getWalletBallance.ts';
export const WalletCard = () => {
  const { data } = useWalletBalance();
  return <DashboardCard></DashboardCard>;
};
