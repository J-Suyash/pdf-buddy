import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    flexRender,
    type ColumnDef,
} from '@tanstack/react-table';
import { getAllQuestions, type Question } from '../api/client';
import { Eye, ChevronLeft, ChevronRight, Search, Filter } from 'lucide-react';
import { cn } from '../utils';

export default function QuestionLibrary() {
    const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
    const [globalFilter, setGlobalFilter] = useState('');
    const [filters, setFilters] = useState({
        year: '',
        course_code: '',
        exam_type: ''
    });

    const { data: questions = [], isLoading } = useQuery({
        queryKey: ['questions', filters, globalFilter],
        queryFn: () => getAllQuestions({ ...filters, search: globalFilter }),
    });

    const columns: ColumnDef<Question>[] = [
        {
            accessorKey: 'course_code',
            header: 'Course',
            cell: ({ row }) => (
                <div>
                    <div className="font-medium font-mono text-primary">{row.original.course_code || '-'}</div>
                    <div className="text-xs text-muted-foreground">{row.original.course_name}</div>
                </div>
            ),
        },
        {
            accessorKey: 'exam_date',
            header: 'Date',
            cell: ({ getValue }) => (
                <span className="text-sm text-muted-foreground font-mono">
                    {getValue() as string || '-'}
                </span>
            ),
        },
        {
            accessorKey: 'question_number',
            header: 'Q#',
            cell: ({ getValue }) => (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold font-mono bg-secondary text-secondary-foreground">
                    {getValue() as string || '-'}
                </span>
            ),
        },
        {
            accessorKey: 'content',
            header: 'Question',
            cell: ({ getValue }) => (
                <div className="max-w-md truncate text-sm text-foreground/80 font-serif">
                    {(getValue() as string)?.substring(0, 100)}...
                </div>
            ),
        },
        {
            accessorKey: 'part',
            header: 'Part',
            cell: ({ getValue }) => {
                const part = getValue() as string;
                return part ? (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-muted text-muted-foreground">
                        Part {part}
                    </span>
                ) : null;
            },
        },
        {
            accessorKey: 'unit',
            header: 'Unit',
            cell: ({ getValue }) => {
                const unit = getValue() as number;
                return unit ? (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-muted text-muted-foreground">
                        Unit {unit}
                    </span>
                ) : null;
            },
        },
        {
            accessorKey: 'is_mcq',
            header: 'Type',
            cell: ({ row }) => {
                const isMcq = row.original.is_mcq;
                return (
                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${isMcq ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-transparent' : 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-transparent'
                        }`}>
                        {isMcq ? 'MCQ' : 'Descriptive'}
                    </span>
                );
            },
        },
        {
            accessorKey: 'marks',
            header: 'Marks',
            cell: ({ getValue }) => (
                <span className="font-semibold font-mono text-foreground">{getValue() as number || '-'}</span>
            ),
        },
        {
            id: 'actions',
            header: 'Actions',
            cell: ({ row }) => (
                <button
                    onClick={() => setSelectedQuestion(row.original)}
                    className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                >
                    <Eye className="w-4 h-4" />
                </button>
            ),
        },
    ];

    const table = useReactTable({
        data: questions,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        state: {
            globalFilter,
        },
        onGlobalFilterChange: setGlobalFilter,
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-7xl mx-auto pt-6">
            <div className="flex flex-col gap-6 animate-fade-in">
                <div>
                    <h1 className="text-4xl font-heading font-bold mb-2 text-foreground">Question Library</h1>
                    <p className="text-muted-foreground">Browse and manage your entire collection of questions.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-card border border-border">
                    <div className="relative group">
                         <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            placeholder="Search questions..."
                            value={globalFilter}
                            onChange={(e) => setGlobalFilter(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-foreground"
                        />
                    </div>
                    
                    <div className="relative group">
                        <Filter className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            placeholder="Course Code"
                            value={filters.course_code}
                            onChange={(e) => setFilters(prev => ({ ...prev, course_code: e.target.value }))}
                            className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-foreground"
                        />
                    </div>

                    <input
                        type="text"
                        placeholder="Year (e.g. 2024)"
                        value={filters.year}
                        onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
                        className="px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-foreground"
                    />
                    
                    <select
                        value={filters.exam_type}
                        onChange={(e) => setFilters(prev => ({ ...prev, exam_type: e.target.value }))}
                        className="px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-muted-foreground"
                    >
                        <option value="">All Exam Types</option>
                        <option value="End Semester">End Semester</option>
                        <option value="Mid Term">Mid Term</option>
                        <option value="Quiz">Quiz</option>
                    </select>
                </div>
            </div>

            <div className="rounded-2xl bg-card border border-border overflow-hidden animate-slide-up shadow-sm">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-muted/50 border-b border-border">
                            {table.getHeaderGroups().map((headerGroup) => (
                                <tr key={headerGroup.id}>
                                    {headerGroup.headers.map((header) => (
                                        <th
                                            key={header.id}
                                            className="px-6 py-4 text-left text-xs font-bold text-muted-foreground uppercase tracking-wider"
                                        >
                                            {flexRender(header.column.columnDef.header, header.getContext())}
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody className="divide-y divide-border">
                            {table.getRowModel().rows.map((row) => (
                                <tr key={row.id} className="hover:bg-muted/50 transition-colors group">
                                    {row.getVisibleCells().map((cell) => (
                                        <td key={cell.id} className="px-6 py-4 text-sm align-top">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                            {questions.length === 0 && (
                                <tr>
                                    <td colSpan={columns.length} className="px-6 py-12 text-center text-muted-foreground">
                                        No questions found matching your criteria.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-muted/20">
                    <div className="text-sm text-muted-foreground font-mono">
                        Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => table.previousPage()}
                            disabled={!table.getCanPreviousPage()}
                            className="p-2 rounded-lg hover:bg-primary hover:text-primary-foreground disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-muted-foreground transition-colors"
                        >
                            <ChevronLeft className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => table.nextPage()}
                            disabled={!table.getCanNextPage()}
                            className="p-2 rounded-lg hover:bg-primary hover:text-primary-foreground disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-muted-foreground transition-colors"
                        >
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Question Detail Modal */}
            {selectedQuestion && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in" onClick={() => setSelectedQuestion(null)}>
                    <div className="bg-card rounded-2xl border border-border max-w-2xl w-full max-h-[80vh] overflow-y-auto p-8 shadow-2xl relative animate-slide-up" onClick={(e) => e.stopPropagation()}>
                        <h2 className="text-3xl font-heading font-bold mb-6 text-foreground">Question Details</h2>

                        <div className="space-y-6">
                            <div className="p-4 bg-muted/30 rounded-xl border border-border">
                                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-2">Question Content</p>
                                <p className="text-lg text-foreground font-serif leading-relaxed">{selectedQuestion.content}</p>
                            </div>

                            {selectedQuestion.is_mcq && selectedQuestion.options && (
                                <div>
                                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wide mb-3">Options</p>
                                    <div className="grid grid-cols-1 gap-3">
                                        {Object.entries(selectedQuestion.options).map(([key, value]) => (
                                            <div key={key} className="flex gap-4 items-center p-3 rounded-lg border border-border/50 bg-card hover:border-primary/50 transition-colors">
                                                <span className="flex items-center justify-center w-8 h-8 rounded-md bg-secondary text-secondary-foreground font-bold font-mono">
                                                    {key}
                                                </span>
                                                <span className="flex-1 text-sm font-medium text-foreground">{value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-2 pt-4 border-t border-border">
                                {selectedQuestion.part && (
                                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-secondary text-secondary-foreground">
                                        PART {selectedQuestion.part}
                                    </span>
                                )}
                                {selectedQuestion.unit && (
                                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-secondary text-secondary-foreground">
                                        UNIT {selectedQuestion.unit}
                                    </span>
                                )}
                                {selectedQuestion.marks && (
                                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-secondary text-secondary-foreground">
                                        {selectedQuestion.marks} MARKS
                                    </span>
                                )}
                            </div>

                            <button
                                onClick={() => setSelectedQuestion(null)}
                                className="w-full py-3 px-4 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors font-bold mt-4"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
