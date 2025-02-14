import React, { useState } from 'react';
import {
  Checkbox,
  Dialog,
  DialogContent,
  FormControlLabel,
  TextField,
  Typography,
} from '@mui/material';
import { DialogHeader } from '@/components/DialogHeader';
import { DialogFooter } from '@/components/DialogFooter';
import { useBuyStock } from '@/api/buyStock.ts';
import { OrderType } from '@/lib/enums.ts';
import './PurchaseStockDialog.scss';

interface PurchaseStockDialogProps {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  stockId: number;
  stockName: string;
  price: number;
}

export const PurchaseStockDialog = ({
  isOpen,
  setIsOpen,
  stockId,
  stockName,
  price,
}: PurchaseStockDialogProps) => {
  const buyStock = useBuyStock();
  const [quantity, setQuantity] = useState('');
  const [isLimit, setIsLimit] = useState(false);

  const handleSubmit = async () => {
    try {
      await buyStock.mutateAsync({
        stockId,
        orderType: isLimit ? OrderType.LIMIT : OrderType.MARKET,
        quantity: Number(quantity),
        price,
      });
    } catch (e) {}
  };

  return (
    <Dialog
      open={isOpen}
      slotProps={{ paper: { className: 'purchase-stock-dialog' } }}
    >
      <DialogHeader title="Purchase stock" />
      <DialogContent>
        <Typography variant="subtitle2">{`Stock: ${stockName}`}</Typography>
        <FormControlLabel
          control={
            <Checkbox checked={isLimit} onChange={() => setIsLimit(!isLimit)} />
          }
          label="Limit order?"
        />
        {isLimit && <TextField label="Price"></TextField>}
        <TextField
          label="Quantity"
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        ></TextField>
      </DialogContent>
      <DialogFooter onSubmit={() => {}} onCancel={() => setIsOpen(false)} />
    </Dialog>
  );
};
