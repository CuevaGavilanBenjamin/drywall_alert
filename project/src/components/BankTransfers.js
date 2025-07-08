import React, { useState } from 'react';

const BankTransfers = ({ accounts }) => {
  const [fromAccount, setFromAccount] = useState('');
  const [toAccount, setToAccount] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');

  const handleTransfer = (e) => {
    e.preventDefault();
    // Lógica de simulación de transferencia
    console.log({ fromAccount, toAccount, amount, description });
    alert('Transferencia simulada con éxito!');
    // Resetear formulario
    setFromAccount('');
    setToAccount('');
    setAmount('');
    setDescription('');
  };

  return (
    <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Realizar Transferencia</h2>

      <form onSubmit={handleTransfer} className="bg-white p-8 rounded-xl shadow-md border border-gray-200 max-w-lg mx-auto">
        <div className="mb-6">
          <label htmlFor="fromAccount" className="block text-gray-700 text-sm font-medium mb-2">Cuenta Origen</label>
          <select
            id="fromAccount"
            value={fromAccount}
            onChange={(e) => setFromAccount(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            required
          >
            <option value="">Selecciona una cuenta</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.name} ({account.number}) - ${account.balance.toLocaleString('es-MX')}
              </option>
            ))}
          </select>
        </div>

        <div className="mb-6">
          <label htmlFor="toAccount" className="block text-gray-700 text-sm font-medium mb-2">Cuenta Destino</label>
          <input
            type="text"
            id="toAccount"
            value={toAccount}
            onChange={(e) => setToAccount(e.target.value)}
            placeholder="Número de cuenta o CLABE"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            required
          />
        </div>

        <div className="mb-6">
          <label htmlFor="amount" className="block text-gray-700 text-sm font-medium mb-2">Monto</label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Ej. 100.00"
            min="0.01"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            required
          />
        </div>

        <div className="mb-6">
          <label htmlFor="description" className="block text-gray-700 text-sm font-medium mb-2">Concepto</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Descripción de la transferencia (opcional)"
            rows="3"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition resize-none"
          ></textarea>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md text-lg font-semibold"
        >
          Confirmar Transferencia
        </button>
      </form>
    </div>
  );
};

export default BankTransfers;