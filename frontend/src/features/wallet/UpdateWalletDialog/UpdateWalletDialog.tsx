import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  Typography,
  Snackbar,
  Alert,
} from '@mui/material';
import { useUpdateWallet } from '@/api/updateWallet.ts';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import './UpdateWalletDialog.scss';
import { SlideTransition } from '@/components/SlideTransition';

interface UpdateWalletDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

export const UpdateWalletDialog = ({
  isOpen,
  setIsOpen,
}: UpdateWalletDialogProps) => {
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [error, setError] = useState<undefined | string>(undefined);

  const updateWallet = useUpdateWallet({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
        setError(undefined);
      },
      onError: (err) => {
        setError(err.response?.data.detail ?? 'An unknown error occurred');
        setShowSnackbar(true);
      },
    },
  });
  const [amount, setAmount] = useState('');

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
    <>
      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSnackbar(false)}
        TransitionComponent={SlideTransition}
      >
        <Alert
          onClose={() => setShowSnackbar(false)}
          variant="filled"
          severity="error"
        >
          {error}
        </Alert>
      </Snackbar>
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
    </>
  );
};
