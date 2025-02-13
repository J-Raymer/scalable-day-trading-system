import React from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { useWalletBalance } from '@/api/getWalletBallance.ts';
import { Typography } from '@mui/material';
import './WalletCard.scss';

export const WalletCard = () => {
  const { data } = useWalletBalance();
  return (
    <DashboardCard>
      <Typography variant="h5" component="h2">
        Wallet
      </Typography>
      <Typography variant="body2" color="textSecondary">
        {`Your balance is $${data?.balance ?? ''}`}
      </Typography>
    </DashboardCard>
  );
};
