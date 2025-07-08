import React from 'react';

const BankDashboard = ({ accounts, recentTransactions }) => {
  return (
    <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Resumen General</h2>

      {/* Sección de Cuentas */}
      <div className="mb-8">
        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Mis Cuentas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200">
              <h4 className="text-xl font-medium text-gray-800 mb-2">{account.name}</h4>
              <p className="text-gray-600 text-sm mb-1">No. Cuenta: {account.number}</p>
              <p className="text-3xl font-bold text-blue-600">${account.balance.toLocaleString('es-MX')}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Sección de Transacciones Recientes */}
      <div>
        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Transacciones Recientes</h3>
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
          {recentTransactions.length > 0 ? (
            <ul className="space-y-4">
              {recentTransactions.map((transaction) => (
                <li key={transaction.id} className="flex justify-between items-center border-b pb-3 last:border-b-0 last:pb-0">
                  <div>
                    <p className="text-lg font-medium text-gray-800">{transaction.description}</p>
                    <p className="text-sm text-gray-500">{transaction.date}</p>
                  </div>
                  <p className={`text-lg font-semibold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toLocaleString('es-MX')}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-center py-4">No hay transacciones recientes.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default BankDashboard;