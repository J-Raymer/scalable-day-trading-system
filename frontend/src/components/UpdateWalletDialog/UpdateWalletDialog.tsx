import React, { useState } from 'react';
import { Dialog, DialogContent, TextField, Typography } from '@mui/material';
import { useUpdateWallet } from '@/api/updateWallet.ts';
import { DialogHeader } from '../DialogHeader';
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
      },
      onError: (error) => {
        onError(error.message);
      },
    },
  });
  const [amount, setAmount] = useState('');

  const handleSubmit = async () => {
    try {
      await updateWallet.mutateAsync({ amount: Number(amount) });
    } catch (e) {
      if (e instanceof Error) {
        onError(e.message);
      } else {
        onError('An unknown error occurred');
      }
    }
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
          onChange={(e) => setAmount(e.target.value)}
        />
      </DialogContent>

      <DialogFooter onSubmit={handleSubmit} onCancel={() => setIsOpen(false)} />
    </Dialog>
  );
};
