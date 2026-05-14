import { AlertCircle, CheckCircle } from 'lucide-react';

export default function LoginMessages({ success, error }) {
  return (
    <>
      {/* Success Message with Animation */}
      {success && (
        <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl flex items-start gap-3 animate-bounce-in">
          <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-green-800">Login Successful! 🎉</p>
            <p className="text-xs text-green-600 mt-1">Redirecting to your dashboard...</p>
          </div>
        </div>
      )}

      {/* Error Message with Animation */}
      {error && (
        <div className="mb-6 p-4 bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-200 rounded-2xl flex items-start gap-3 animate-shake">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-bold text-red-800">Oops! Something went wrong</p>
            <p className="text-xs text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}
    </>
  );
}

