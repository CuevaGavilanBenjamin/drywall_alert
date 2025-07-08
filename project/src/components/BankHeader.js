import React from 'react';

const BankHeader = ({ userName, onLogout }) => {
  return (
    <header className="w-full bg-white shadow-sm p-4 flex justify-between items-center rounded-b-2xl">
      <div className="flex items-center">
        <div className="text-2xl font-bold text-gray-800">BankFlow</div>
        <span className="ml-4 text-lg text-gray-600 hidden sm:block">Bienvenido, {userName}</span>
      </div>
      <button
        onClick={onLogout}
        className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors shadow-md"
      >
        Cerrar Sesión
      </button>
    </header>
  );
};

export default BankHeader;