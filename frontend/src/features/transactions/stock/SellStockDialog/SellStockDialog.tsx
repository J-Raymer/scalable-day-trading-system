import React, { useState } from 'react';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import {
  Alert,
  Dialog,
  DialogContent,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import { SlideTransition } from '@/components/SlideTransition';
import { usePlaceOrder } from '@/api/placeOrder.ts';

interface CancelOrderDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  stockId: number | undefined;
  setCurrentId: React.Dispatch<React.SetStateAction<number | undefined>>;
}

interface FormErrors {
  price: string | undefined;
  quantity: string | undefined;
}

export const SellStockDialog = ({
  isOpen,
  setIsOpen,
  stockId,
  setCurrentId,
}: CancelOrderDialogProps) => {
  const [showError, setShowError] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [formErrors, setFormErrors] = useState<FormErrors>({
    price: undefined,
    quantity: undefined,
  });

  const sellStock = usePlaceOrder({
    mutationConfig: {
      onSuccess: () => {
        setIsOpen(false);
        setCurrentId(undefined);
        setQuantity('');
        setPrice('');
      },
      onError: (error) => {
        setError(error.response?.data.detail ?? 'An unknown error occurred');
        setShowError(true);
      },
    },
  });

  const handleValidate = (price: number, quantity: number) => {
    let error = false;
    // Use a separate variable to update state properly
    const newFormErrors: FormErrors = { ...formErrors };
    if (quantity <= 0) {
      newFormErrors.quantity = 'Quantity must be greater than 0';
      error = true;
    }
    if (price <= 0) {
      newFormErrors.price = 'Price must be greater than 0';
      error = true;
    }
    setFormErrors(newFormErrors);
    return error;
  };

  const handleSubmit = async () => {
    if (stockId === undefined) {
      return;
    }

    const priceAsNum = Number(price);
    const quantityAsNum = Number(quantity);
    const error = handleValidate(priceAsNum, quantityAsNum);
    if (error) {
      setError('Error, missing stock id');
      setShowError(true);
      return;
    }

    try {
      await sellStock.mutateAsync({
        stockId,
        quantity: quantityAsNum,
        price: priceAsNum,
        isBuy: false,
      });
    } catch (e) {}
  };

  const handleCloseError = () => {
    setError(undefined);
    setShowError(false);
  };

  const handleCancel = () => {
    setPrice('');
    setQuantity('');
    setFormErrors({ quantity: undefined, price: undefined });
    setIsOpen(false);
  };

  return (
    <>
      <Dialog open={isOpen}>
        <DialogHeader title={'Sell stock'} />
        <DialogContent>
          <Typography>{`Stock id: ${stockId}`}</Typography>
          <Typography>
            Enter the quantity you would like to sell and the price at which you
            would like to automatically sell it at.
          </Typography>
          <TextField
            label="Quantity"
            type="number"
            value={quantity}
            error={formErrors.quantity !== undefined}
            helperText={formErrors.quantity}
            onChange={(e) => setQuantity(e.target.value)}
          />
          <TextField
            label="Price"
            type="number"
            value={price}
            error={formErrors.price !== undefined}
            helperText={formErrors.price}
            onChange={(e) => setPrice(e.target.value)}
          />
        </DialogContent>
        <DialogFooter onSubmit={handleSubmit} onCancel={handleCancel} />
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
