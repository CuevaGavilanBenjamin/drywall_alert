export const defaultAccounts = [
  {
    id: '1',
    name: 'Cuenta de Ahorro',
    number: '1234567890',
    type: 'Ahorro',
    balance: 15000.50,
  },
  {
    id: '2',
    name: 'Cuenta Corriente',
    number: '0987654321',
    type: 'Corriente',
    balance: 5000.75,
  },
  {
    id: '3',
    name: 'Tarjeta de Crédito',
    number: '4567-XXXX-XXXX-1234',
    type: 'Crédito',
    balance: -2500.00, // Saldo negativo para crédito
  },
];

export const defaultTransactions = [
  {
    id: 't1',
    description: 'Compra en Supermercado',
    date: '2023-10-26',
    amount: 350.20,
    type: 'expense',
    accountId: '1',
  },
  {
    id: 't2',
    description: 'Depósito de Nómina',
    date: '2023-10-25',
    amount: 12000.00,
    type: 'income',
    accountId: '1',
  },
  {
    id: 't3',
    description: 'Pago de Servicio de Luz',
    date: '2023-10-24',
    amount: 850.00,
    type: 'expense',
    accountId: '2',
  },
  {
    id: 't4',
    description: 'Retiro en Cajero',
    date: '2023-10-23',
    amount: 500.00,
    type: 'expense',
    accountId: '1',
  },
  {
    id: 't5',
    description: 'Transferencia Recibida',
    date: '2023-10-22',
    amount: 2000.00,
    type: 'income',
    accountId: '2',
  },
];