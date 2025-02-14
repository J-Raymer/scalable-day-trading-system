import React, { useState } from 'react';
import { Dialog, DialogContent, TextField, Typography } from '@mui/material';
import { useUpdateWallet } from '@/api/updateWallet.ts';
import { DialogHeader } from '../DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import './UpdateWalletDialog.scss';

interface UpdateWalletDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export const UpdateWalletDialog = ({
  isOpen,
  setIsOpen,
}: UpdateWalletDialogProps) => {
  const updateWallet = useUpdateWallet({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
      },
    },
  });
  const [amount, setAmount] = useState('');

  const handleSubmit = async () => {
    try {
      await updateWallet.mutateAsync({ amount: Number(amount) });
    } catch (e) {}
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
