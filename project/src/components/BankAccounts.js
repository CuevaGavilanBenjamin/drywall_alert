import React from 'react';

const BankAccounts = ({ accounts }) => {
  return (
    <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Mis Cuentas Bancarias</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map((account) => (
          <div key={account.id} className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200">
            <h4 className="text-xl font-medium text-gray-800 mb-2">{account.name}</h4>
            <p className="text-gray-600 text-sm mb-1">Tipo: {account.type}</p>
            <p className="text-gray-600 text-sm mb-1">No. Cuenta: {account.number}</p>
            <p className="text-3xl font-bold text-blue-600 mt-3">${account.balance.toLocaleString('es-MX')}</p>
            <button className="w-full mt-4 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors shadow-md">
              Ver Detalles
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <button className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors shadow-md text-lg">
          Abrir Nueva Cuenta
        </button>
      </div>
    </div>
  );
};

export default BankAccounts;