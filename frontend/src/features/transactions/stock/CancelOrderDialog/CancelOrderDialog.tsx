import React, { useState } from 'react';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import {
  Alert,
  Dialog,
  DialogContent,
  Typography,
  Snackbar,
} from '@mui/material';
import { useCancelOrder } from '@/api/cancelOrder.ts';
import { ButtonColor } from '@/lib/enums.ts';
import { SlideTransition } from '@/components/SlideTransition';

interface CancelOrderDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  stockTxId: number | undefined;
  setCurrentId: React.Dispatch<React.SetStateAction<number | undefined>>;
}

export const CancelOrderDialog = ({
  isOpen,
  setIsOpen,
  stockTxId,
  setCurrentId,
}: CancelOrderDialogProps) => {
  const [showError, setShowError] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const cancelOrder = useCancelOrder({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
        setCurrentId(undefined);
      },
      onError: (error) => {
        setError(error.response?.data.detail ?? 'An unknown error occurred');
        setShowError(true);
      },
    },
  });

  const handleSubmit = async () => {
    if (stockTxId === undefined) {
      return;
    }
    try {
      await cancelOrder.mutateAsync({ stockTxId });
    } catch (e) {}
  };

  const handleCloseError = () => {
    setError(undefined);
    setShowError(false);
  };

  return (
    <>
      <Dialog open={isOpen}>
        <DialogHeader title={'Cancel order'} />
        <DialogContent>
          <Typography>{`Stock Transaction ID: ${stockTxId}`}</Typography>
          <Alert severity="error">
            Are you sure you want to cancel this transaction? This cannot be
            undone!
          </Alert>
        </DialogContent>
        <DialogFooter
          onSubmit={handleSubmit}
          onCancel={() => setIsOpen(false)}
          color={ButtonColor.ERROR}
        />
      </Dialog>
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={handleCloseError}
        TransitionComponent={SlideTransition}
      >
        <Alert onClose={handleCloseError} variant="filled" severity="error">
          {error}
        </Alert>
      </Snackbar>
    </>
  );
};
