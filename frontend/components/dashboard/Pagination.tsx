"use client";

import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
}

export function Pagination({ currentPage, totalPages }: PaginationProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Don't render if only one page or no pages
  if (totalPages <= 1) {
    return null;
  }

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', page.toString());
    router.push(`${pathname}?${params.toString()}`);
  };

  const goToPrevious = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const goToNext = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  return (
    <div className="flex items-center justify-center gap-4 py-8">
      <button
        onClick={goToPrevious}
        disabled={isFirstPage}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
          ${isFirstPage
            ? 'text-slate-400 cursor-not-allowed bg-slate-50'
            : 'text-slate-700 hover:bg-slate-100 bg-white border border-slate-300'
          }
        `}
        aria-label="Previous page"
      >
        <ChevronLeft className="w-4 h-4" />
        <span>Previous</span>
      </button>

      <div className="text-sm text-slate-600 font-medium">
        Page <span className="text-slate-900 font-semibold">{currentPage}</span> of{' '}
        <span className="text-slate-900 font-semibold">{totalPages}</span>
      </div>

      <button
        onClick={goToNext}
        disabled={isLastPage}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
          ${isLastPage
            ? 'text-slate-400 cursor-not-allowed bg-slate-50'
            : 'text-slate-700 hover:bg-slate-100 bg-white border border-slate-300'
          }
        `}
        aria-label="Next page"
      >
        <span>Next</span>
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}
