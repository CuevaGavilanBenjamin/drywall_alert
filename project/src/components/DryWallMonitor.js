import React, { useState, useEffect } from 'react';

const DryWallMonitor = () => {
  const [dryWallData, setDryWallData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDryWallData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/drywall/status');
      if (!response.ok) throw new Error('Error fetching DryWall data');
      
      const data = await response.json();
      setDryWallData(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching DryWall data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDryWallData();
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchDryWallData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
        <div className="animate-pulse">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Monitor DryWall</h2>
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Monitor DryWall</h2>
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
          <p className="font-bold">Error de Conexión</p>
          <p>{error}</p>
          <button 
            onClick={fetchDryWallData}
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Monitor DryWall Alert</h2>
        <button 
          onClick={fetchDryWallData}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Estado del Sistema */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Estado del Sistema</h3>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-green-600 font-medium">Online</span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            SFTP: {dryWallData?.drywall_integration?.sftp_server || 'Unknown'}
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Archivos Recibidos</h3>
          <div className="text-2xl font-bold text-blue-600">
            {dryWallData?.files_received?.total_count || 0}
          </div>
          <p className="text-sm text-gray-500">
            {(dryWallData?.files_received?.total_size_bytes / 1024 / 1024).toFixed(2) || 0} MB
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Última Actualización</h3>
          <div className="text-sm text-gray-600">
            {new Date(dryWallData?.timestamp).toLocaleString('es-ES') || 'N/A'}
          </div>
        </div>
      </div>

      {/* Lista de Archivos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 bg-gray-100 border-b">
          <h3 className="text-lg font-semibold text-gray-800">Archivos de Sensores Recibidos</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Archivo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tamaño
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dryWallData?.files_received?.files?.length > 0 ? (
                dryWallData.files_received.files.map((file, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900">
                          {file.name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        file.type === 'csv' ? 'bg-green-100 text-green-800' : 
                        file.type === 'json' ? 'bg-blue-100 text-blue-800' : 
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {file.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(file.modified).toLocaleString('es-ES')}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                    <div className="flex flex-col items-center">
                      <div className="text-4xl mb-2">📡</div>
                      <p>No se han recibido archivos del cliente DryWall</p>
                      <p className="text-sm mt-1">Los archivos aparecerán automáticamente cuando se suban via SFTP</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Información Técnica */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-md font-semibold text-blue-800 mb-2">Información de Integración</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong>Servidor SFTP:</strong> localhost:22<br/>
            <strong>API REST:</strong> localhost:8000<br/>
            <strong>Directorio Upload:</strong> {dryWallData?.drywall_integration?.upload_directory}
          </div>
          <div>
            <strong>Cliente:</strong> DryWall Alert<br/>
            <strong>Protocolo:</strong> SFTP + SSH Keys<br/>
            <strong>Estado:</strong> <span className="text-green-600">✅ Operativo</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DryWallMonitor;
