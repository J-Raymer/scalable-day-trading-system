import React, { useState } from 'react';
import {
  Checkbox,
  Dialog,
  DialogContent,
  FormControlLabel,
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
  stockId: number;
  stockName: string;
  price: number;
}

interface FormErrors {
  limit: string | undefined;
  quantity: string | undefined;
}

export const PurchaseStockDialog = ({
  isOpen,
  setIsOpen,
  stockId,
  stockName,
  price,
}: PurchaseStockDialogProps) => {
  const [quantity, setQuantity] = useState('');
  const [limit, setLimit] = useState('');
  const [isLimit, setIsLimit] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [formErrors, setFormErrors] = useState<FormErrors>({
    limit: undefined,
    quantity: undefined,
  });

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

  const handleValidate = (quantity: number, limit: number) => {
    let error = false;
    // Use a separate variable to update state properly
    const newFormErrors: FormErrors = { ...formErrors };

    if (quantity <= 0) {
      newFormErrors.quantity = 'Must be greater than 0';
      error = true;
    }
    if (isLimit && limit <= 0) {
      newFormErrors.limit = 'Limit must be greater than 0';
      error = true;
    }

    setFormErrors(newFormErrors);
    return error;
  };

  const handleSubmit = async () => {
    const quantityAsNum = Number(quantity);
    const limitAsNum = Number(limit);
    const error = handleValidate(quantityAsNum, limitAsNum);
    if (error) {
      return;
    }

    try {
      await buyStock.mutateAsync({
        stockId,
        orderType: isLimit ? OrderType.LIMIT : OrderType.MARKET,
        quantity: Number(quantity),
        price: isLimit ? Number(limit) : price,
      });
    } catch (e) {}
  };

  const handleClose = () => {
    setFormErrors({ quantity: undefined, limit: undefined });
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
        <Typography variant="subtitle2">{`Current best Price: ${price}`}</Typography>
        <Typography>
          If this is a limit order enter the price you would like to purchase
          the stock at, otherwise the current best prices will be used. If
          there is insufficient quantity at the best price, the next best price will be used.
        </Typography>
        <FormControlLabel
          control={
            <Checkbox
              className="checkbox"
              checked={isLimit}
              onChange={() => setIsLimit(!isLimit)}
            />
          }
          label="Limit order"
        />
        {isLimit && (
          <TextField
            label="Price"
            type="number"
            value={limit}
            error={formErrors['limit'] !== undefined}
            helperText={formErrors['limit']}
            onChange={(e) => setLimit(e.target.value)}
          />
        )}
        <TextField
          label="Quantity"
          type="number"
          value={quantity}
          error={formErrors['quantity'] !== undefined}
          helperText={formErrors['quantity']}
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
