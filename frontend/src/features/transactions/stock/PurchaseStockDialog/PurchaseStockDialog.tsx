import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  Typography,
  Snackbar,
  Alert,
} from '@mui/material';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import { usePlaceOrder } from '@/api/placeOrder.ts';
import { OrderType } from '@/lib/enums.ts';
import './PurchaseStockDialog.scss';
import { SlideTransition } from '@/components/SlideTransition';

interface PurchaseStockDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  stockId: number | undefined;
  stockName: string;
  price: number | undefined;
}

export const PurchaseStockDialog = ({
  isOpen,
  setIsOpen,
  stockId,
  stockName,
  price,
}: PurchaseStockDialogProps) => {
  const [quantity, setQuantity] = useState('');
  const [error, setError] = useState<string | undefined>(undefined);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [formError, setFormError] = useState<string | undefined>(undefined);

  const buyStock = usePlaceOrder({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
      },
      onError: (error) => {
        setError(error.response?.data.detail ?? 'An unknown error occurred');
        setShowSnackbar(true);
      },
    },
  });

  const handleSubmit = async () => {
    const quantityAsNum = Number(quantity);

    if (quantityAsNum <= 0) {
      setFormError('Must be greater than 0');
      return;
    }

    if (stockId === undefined) {
      setError('Error, missing stock Id');
      setShowSnackbar(true);
      return;
    }
    if (price === undefined) {
      setError('Error, missing price');
      return;
    }

    try {
      await buyStock.mutateAsync({
        stockId,
        quantity: quantityAsNum,
        price: price,
        isBuy: true,
      });
    } catch (e) {}
  };

  const handleClose = () => {
    setFormError(undefined);
    setIsOpen(false);
  };

  return (
    <Dialog
      open={isOpen}
      slotProps={{ paper: { className: 'purchase-stock-dialog' } }}
    >
      <DialogHeader title="Purchase stock" />
      <DialogContent>
        <Typography variant="subtitle2">{`Stock: ${stockName}`}</Typography>
        <Typography variant="subtitle2">{`Current best price: ${price}`}</Typography>
        <Typography>Enter the quantity you would like to purchase.</Typography>
        <TextField
          label="Quantity"
          type="number"
          value={quantity}
          error={formError !== undefined}
          helperText={formError}
          onChange={(e) => setQuantity(e.target.value)}
        />
      </DialogContent>
      <DialogFooter onSubmit={handleSubmit} onCancel={handleClose} />
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
    </Dialog>
  );
};
