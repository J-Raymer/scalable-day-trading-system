import React, { useState } from 'react';
import { Dialog, DialogContent, TextField, Typography } from '@mui/material';
import { useUpdateWallet } from '@/api/updateWallet.ts';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import './UpdateWalletDialog.scss';

interface UpdateWalletDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onError: (message: string) => void;
}

export const UpdateWalletDialog = ({
  isOpen,
  setIsOpen,
  onError,
}: UpdateWalletDialogProps) => {
  const updateWallet = useUpdateWallet({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
        setError(undefined);
      },
      onError: (error) => {
        onError(error.response?.data.detail ?? 'An unknown error occurred');
      },
    },
  });
  const [amount, setAmount] = useState('');
  const [error, setError] = useState<undefined | string>(undefined);

  const handleSubmit = async () => {
    const amountAsNum = Number(amount);
    if (amountAsNum <= 0) {
      setError('Amount must be greater than 0');
      return;
    }
    try {
      await updateWallet.mutateAsync({ amount: amountAsNum });
    } catch (e) {}
  };

  const handleClose = () => {
    setError(undefined);
    setIsOpen(false);
    setAmount('');
  };

  return (
    <Dialog
      open={isOpen}
      slotProps={{ paper: { className: 'update-wallet-dialog' } }}
    >
      <DialogHeader title={'Add money to wallet'}></DialogHeader>
      <DialogContent>
        <Typography>
          Enter the amount you would like to add to your current balance.
        </Typography>
        <TextField
          label="Amount to add"
          type="number"
          value={amount}
          error={error !== undefined}
          helperText={error ?? ''}
          onChange={(e) => setAmount(e.target.value)}
        />
      </DialogContent>
      <DialogFooter onSubmit={handleSubmit} onCancel={handleClose} />
    </Dialog>
  );
};
