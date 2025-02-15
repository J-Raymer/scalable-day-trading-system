import React, { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard/DashboardCard.tsx';
import { useWalletBalance } from '@/api/getWalletBallance.ts';
import { Button, Typography } from '@mui/material';
import { UpdateWalletDialog } from '../UpdateWalletDialog';
import './WalletCard.scss';

interface WalletCardProps {
  onError: (message: string) => void;
}

export const WalletCard = ({ onError }: WalletCardProps) => {
  const { data, error } = useWalletBalance();

  if (error && typeof error === 'object' && 'message' in error) {
    onError((error as { message: string }).message);
  }
  const [open, setOpen] = useState(false);

  return (
    <DashboardCard className="wallet-card">
      <UpdateWalletDialog isOpen={open} setIsOpen={setOpen} onError={onError} />
      <div>
        <Typography variant="h5" component="h2">
          Wallet
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {`Your balance is $${data?.balance ?? ''}`}
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
