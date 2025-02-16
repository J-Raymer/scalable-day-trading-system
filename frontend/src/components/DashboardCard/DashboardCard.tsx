import React, { ReactNode } from 'react';
import { Card, CardActionArea, CardActions, CardContent } from '@mui/material';
import './DashboardCard.scss';

interface DashboardCardProps {
  children: ReactNode;
  className?: string;
}

export const DashboardCard = ({ children, className }: DashboardCardProps) => {
  return (
    <Card>
      <CardContent className={className}>{children}</CardContent>
    </Card>
  );
};
