import { CheckSquare } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        <div className="p-8 pb-0">
          <div className="flex justify-center mb-8">
            <div className="flex items-center gap-2 text-indigo-600 font-bold text-2xl">
              <CheckSquare className="w-8 h-8" />
              <span>TaskFlow</span>
            </div>
          </div>
        </div>
        {children}
        <div className="bg-slate-50 p-4 border-t border-slate-100 text-center text-xs text-slate-400">
          © 2024 TaskFlow AI. Secure & Encrypted.
        </div>
      </div>
    </div>
  );
}
