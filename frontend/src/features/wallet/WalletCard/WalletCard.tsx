import React, { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { useWalletBalance } from '@/api/getWalletBallance.ts';
import { Button, Typography, Skeleton } from '@mui/material';
import { UpdateWalletDialog } from '@/features/wallet/UpdateWalletDialog';
import './WalletCard.scss';

export const WalletCard = () => {
  const { data, isLoading } = useWalletBalance();

  const [open, setOpen] = useState(false);

  return (
    <DashboardCard className="wallet-card">
      <UpdateWalletDialog isOpen={open} setIsOpen={setOpen} />
      <div>
        <Typography variant="h5" component="h2">
          Wallet
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {isLoading ? (
            <Skeleton />
          ) : (
            <>
              {data?.balance !== undefined
                ? `Your balance is $${data?.balance}`
                : 'An error occurred fetching wallet balance'}
            </>
          )}
        </Typography>
      </div>
      <Button
        fullWidth
        variant="contained"
        size={'small'}
        onClick={() => setOpen(true)}
      >
        Add money to wallet
      </Button>
    </DashboardCard>
  );
};
