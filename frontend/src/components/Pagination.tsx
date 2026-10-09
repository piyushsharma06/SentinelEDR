import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  page: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (newPage: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  page,
  totalPages,
  totalItems,
  onPageChange,
}) => {
  if (totalPages <= 1 && totalItems === 0) return null;

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 bg-[#0F172A]/40 text-xs text-slate-400">
      <div>
        Showing page <span className="font-semibold text-slate-200">{page}</span> of{' '}
        <span className="font-semibold text-slate-200">{totalPages || 1}</span> ({totalItems} total records)
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span>Previous</span>
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <span>Next</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
