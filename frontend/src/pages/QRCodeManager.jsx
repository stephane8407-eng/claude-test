import { useState, useEffect } from 'react';
import { qrCodeAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function QRCodeManager() {
  const { user } = useAuth();
  const [qrCodes, setQRCodes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQRCodes();
  }, []);

  const loadQRCodes = async () => {
    try {
      const data = await qrCodeAPI.list(user.village_slug);
      setQRCodes(data);
    } catch (error) {
      console.error('Failed to load QR codes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (qrCode, size) => {
    const url = qrCodeAPI.downloadQR(user.village_slug, qrCode.code, size);
    window.open(url, '_blank');
  };

  if (loading) return <div>Loading QR codes...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">QR Codes</h1>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          Generate QR Code
        </button>
      </div>

      {/* QR Code Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {qrCodes.map((qr) => (
          <div key={qr.id} className="bg-white rounded-lg shadow p-6">
            {/* QR Image Preview */}
            {qr.qr_image_url && (
              <img
                src={qr.qr_image_url}
                alt={qr.name}
                className="w-full h-48 object-contain mb-4"
              />
            )}

            <h3 className="font-semibold text-lg mb-2">{qr.name}</h3>
            <p className="text-sm text-gray-600 mb-4">{qr.description}</p>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Scans:</span>
                <span className="font-semibold">{qr.scan_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last scanned:</span>
                <span className="text-gray-700">
                  {qr.last_scanned_at
                    ? new Date(qr.last_scanned_at).toLocaleDateString()
                    : 'Never'}
                </span>
              </div>
            </div>

            {/* Download Buttons */}
            <div className="mt-4 pt-4 border-t space-y-2">
              <p className="text-xs text-gray-500 mb-2">Download:</p>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleDownload(qr, 'small')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Small
                </button>
                <button
                  onClick={() => handleDownload(qr, 'medium')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Medium
                </button>
                <button
                  onClick={() => handleDownload(qr, 'large')}
                  className="flex-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                >
                  Large
                </button>
              </div>
            </div>

            {/* View Stats Button */}
            <button className="w-full mt-4 px-4 py-2 text-sm text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50">
              View Statistics
            </button>
          </div>
        ))}
      </div>

      {qrCodes.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No QR codes yet. Generate your first one!</p>
        </div>
      )}
    </div>
  );
}
