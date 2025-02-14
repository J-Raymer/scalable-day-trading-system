import React, { useState } from 'react';
import './UpdateWalletDialog.scss';
import { Button, Dialog, TextField } from '@mui/material';
import { useUpdateWallet } from '@/api/updateWallet.ts';
import { DialogHeader } from '../DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';

interface UpdateWalletDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export const UpdateWalletDialog = ({
  isOpen,
  setIsOpen,
}: UpdateWalletDialogProps) => {
  const updateWallet = useUpdateWallet();
  const [amount, setAmount] = useState('');

  const handleSubmit = async () => {
    try {
      // await updateWallet.mutateAsync({ amount });
    } catch (e) {}
  };

  return (
    <Dialog
      open={isOpen}
      slotProps={{ paper: { className: 'update-wallet-dialog' } }}
    >
      <DialogHeader title={'Update Wallet Balance'}></DialogHeader>
      <TextField
        className="content"
        // label="Amount to add"
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <DialogFooter onSubmit={handleSubmit} onCancel={() => setIsOpen(false)} />
    </Dialog>
  );
};
