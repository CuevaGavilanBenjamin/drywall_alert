import React, { useState, useEffect } from 'react';

const DryWallMonitor = () => {
  const [dryWallData, setDryWallData] = useState(null);
  const [sensorData, setSensorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDryWallData = async () => {
    try {
      setLoading(true);
      
      // Obtener estado del sistema
      const statusResponse = await fetch('http://localhost:8000/api/drywall/status');
      if (!statusResponse.ok) throw new Error('Error fetching DryWall status');
      const statusData = await statusResponse.json();
      
      // Obtener datos de sensores procesados
      const sensorResponse = await fetch('http://localhost:8000/api/drywall/sensor-summary');
      if (!sensorResponse.ok) throw new Error('Error fetching sensor data');
      const sensorDataResponse = await sensorResponse.json();
      
      setDryWallData(statusData);
      setSensorData(sensorDataResponse);
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
          <h2 className="text-3xl font-bold text-gray-800 mb-6">🏗️ Monitor DryWall</h2>
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-50 rounded-2xl shadow-lg flex-grow">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">🏗️ Monitor DryWall</h2>
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
        <h2 className="text-3xl font-bold text-gray-800">🏗️ DryWall Alert - Monitor de Humedad</h2>
        <button 
          onClick={fetchDryWallData}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Resumen Ejecutivo */}
      {sensorData && sensorData.summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
            <h3 className="text-sm font-semibold text-gray-600 mb-1">SENSORES ACTIVOS</h3>
            <div className="text-2xl font-bold text-green-600">
              {sensorData.summary.total_sensors}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
            <h3 className="text-sm font-semibold text-gray-600 mb-1">LECTURAS TOTALES</h3>
            <div className="text-2xl font-bold text-blue-600">
              {sensorData.summary.total_readings}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
            <h3 className="text-sm font-semibold text-gray-600 mb-1">HUMEDAD PROMEDIO</h3>
            <div className="text-2xl font-bold text-orange-600">
              {sensorData.summary.average_humidity}%
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
            <h3 className="text-sm font-semibold text-gray-600 mb-1">ALERTAS CRÍTICAS</h3>
            <div className="text-2xl font-bold text-red-600">
              {sensorData.summary.critical_alerts}
            </div>
          </div>
        </div>
      )}

      {/* Estado del Sistema SFTP */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-3">📡 Estado de Conexión</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-green-600 font-medium">SFTP Server Online</span>
          </div>
          <div className="text-sm text-gray-600">
            <strong>Archivos:</strong> {dryWallData?.files_received?.total_count || 0}
          </div>
          <div className="text-sm text-gray-600">
            <strong>Última actualización:</strong> {new Date(dryWallData?.timestamp || Date.now()).toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Datos por Ubicación */}
      {sensorData?.locations && Object.keys(sensorData.locations).length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">📍 Monitoreo por Ubicación</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-2">Ubicación</th>
                  <th className="text-left p-2">Lecturas</th>
                  <th className="text-left p-2">Humedad Prom.</th>
                  <th className="text-left p-2">Alertas</th>
                  <th className="text-left p-2">Última Lectura</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(sensorData.locations).map(([location, data]) => (
                  <tr key={location} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{location}</td>
                    <td className="p-2">{data.readings_count}</td>
                    <td className="p-2">
                      <span className={`font-semibold ${data.avg_humidity > 70 ? 'text-red-600' : data.avg_humidity > 50 ? 'text-orange-600' : 'text-green-600'}`}>
                        {data.avg_humidity}%
                      </span>
                    </td>
                    <td className="p-2">
                      {data.alert_count > 0 ? (
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                          {data.alert_count}
                        </span>
                      ) : (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                          OK
                        </span>
                      )}
                    </td>
                    <td className="p-2 text-xs text-gray-500">
                      {new Date(data.last_reading).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Lecturas Recientes */}
      {sensorData?.recent_readings && sensorData.recent_readings.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">🕒 Lecturas Más Recientes</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-2">Timestamp</th>
                  <th className="text-left p-2">Sensor ID</th>
                  <th className="text-left p-2">Ubicación</th>
                  <th className="text-left p-2">Humedad</th>
                  <th className="text-left p-2">Nivel de Alerta</th>
                </tr>
              </thead>
              <tbody>
                {sensorData.recent_readings.slice(0, 10).map((reading, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="p-2 text-xs font-mono">
                      {new Date(reading.timestamp).toLocaleString()}
                    </td>
                    <td className="p-2 font-medium text-blue-600">{reading.sensor_id}</td>
                    <td className="p-2">{reading.location}</td>
                    <td className="p-2">
                      <span className={`font-semibold ${reading.humidity_percent > 70 ? 'text-red-600' : reading.humidity_percent > 50 ? 'text-orange-600' : 'text-green-600'}`}>
                        {reading.humidity_percent}%
                      </span>
                    </td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        reading.alert_level === 'HIGH' ? 'bg-red-100 text-red-800' :
                        reading.alert_level === 'MEDIUM' ? 'bg-orange-100 text-orange-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {reading.alert_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Footer con información del sistema */}
      <div className="mt-6 text-center text-xs text-gray-500">
        💼 Sistema Bancario - Monitoreo de Cliente DryWall Alert | 
        🔄 Actualización automática cada 30 segundos |
        🔐 Conexión segura vía SFTP
      </div>
    </div>
  );
};

export default DryWallMonitor;