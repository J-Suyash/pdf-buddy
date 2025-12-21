import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { searchQuestions, searchDatalabChunks, type SearchResult, type DatalabSearchResult } from '../api/client';
import { Search as SearchIcon, Sparkles, FileText, ArrowRight, BrainCircuit, FileStack } from 'lucide-react';
import { cn } from '../utils';

export default function Search() {
    const [query, setQuery] = useState('');
    const [searchType, setSearchType] = useState<'datalab' | 'standard'>('datalab');

    const searchMutation = useMutation({
        mutationFn: async (q: string) => {
            if (searchType === 'datalab') {
                return searchDatalabChunks(q, 20);
            }
            return searchQuestions(q, 20);
        },
    });

    const handleSearch = () => {
        if (query.trim()) {
            searchMutation.mutate(query);
        }
    };

    return (
        <div className="space-y-12 max-w-5xl mx-auto">
            {/* Header Section */}
            <div className="text-center space-y-4 pt-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm font-medium mb-4 animate-fade-in">
                    <Sparkles className="w-4 h-4" />
                    <span>AI-Powered Semantic Search</span>
                </div>
                <h1 className="text-6xl font-heading font-bold tracking-tight text-foreground mb-6">
                    Find Exact Questions
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
                    Search through thousands of university question papers using natural language.
                </p>
            </div>

             <div className="flex justify-center">
                <div className="bg-card border border-border p-1 rounded-xl inline-flex shadow-sm">
                    <button
                        className={cn(
                            "px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                            searchType === 'datalab'
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground hover:bg-muted"
                        )}
                        onClick={() => {
                            setSearchType('datalab');
                            searchMutation.reset();
                        }}
                    >
                        <BrainCircuit className="w-4 h-4" />
                        DataLab (Enhanced OCR)
                    </button>
                    <button
                        className={cn(
                            "px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                            searchType === 'standard'
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground hover:bg-muted"
                        )}
                        onClick={() => {
                            setSearchType('standard');
                            searchMutation.reset();
                        }}
                    >
                        <FileStack className="w-4 h-4" />
                        Standard PDF
                    </button>
                </div>
            </div>

            {/* Search Bar */}
            <div className="relative max-w-3xl mx-auto group">
                <div className="relative flex items-center bg-card border border-border rounded-2xl p-2 shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-all">
                    <div className="pl-4 text-muted-foreground">
                        <SearchIcon className="w-6 h-6" />
                    </div>
                    <input
                        type="text"
                        placeholder={searchType === 'datalab' ? "Search for content inside documents..." : "e.g., Explain binary search tree algorithms..."}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        className="flex-1 px-4 py-4 bg-transparent border-none text-lg text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-0 font-medium"
                    />
                    <button
                        onClick={handleSearch}
                        disabled={searchMutation.isPending}
                        className="px-8 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all font-semibold flex items-center gap-2"
                    >
                        {searchMutation.isPending ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <>
                                Search <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Results Section */}
            <div className="space-y-6">
                {searchMutation.isError && (
                    <div className="p-6 bg-destructive/10 border border-destructive/20 text-destructive rounded-xl text-center">
                        Search failed. Please try again.
                    </div>
                )}

                {searchMutation.data && searchMutation.data.length === 0 && (
                    <div className="text-center py-20 opacity-50">
                        <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                        <p className="text-xl text-muted-foreground font-light">No results found.</p>
                    </div>
                )}

                {searchMutation.data && searchMutation.data.length > 0 && (
                    <>
                        <div className="flex items-center justify-between text-sm text-muted-foreground px-2">
                            <span>Found {searchMutation.data.length} results</span>
                            <span>Sorted by relevance</span>
                        </div>
                        <div className="grid gap-6">
                            {searchMutation.data.map((result: SearchResult | DatalabSearchResult, index: number) => {
                                const isDatalab = 'text' in result;
                                const content = isDatalab ? (result as DatalabSearchResult).text : (result as SearchResult).content;
                                
                                return (
                                <div 
                                    key={result.id} 
                                    className="group relative rounded-2xl bg-card border border-border p-6 hover:border-primary/50 hover:shadow-md transition-all duration-300 animate-slide-up"
                                    style={{ animationDelay: `${index * 50}ms` }}
                                >
                                    {/* Relevance Score Indicator */}
                                    <div className="absolute top-6 right-6 flex flex-col items-end">
                                        <span className={cn(
                                            "text-2xl font-bold font-heading",
                                            result.score > 0.8 ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"
                                        )}>
                                            {Math.round(result.score * 100)}%
                                        </span>
                                        <span className="text-xs text-muted-foreground font-mono">MATCH</span>
                                    </div>

                                    {/* Metadata Chips */}
                                    <div className="flex flex-wrap gap-2 mb-4 pr-20">
                                        {isDatalab ? (
                                            <>
                                                <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-secondary text-secondary-foreground uppercase tracking-wider">
                                                    Page {(result as DatalabSearchResult).page_num}
                                                </span>
                                                {(result as DatalabSearchResult).block_type && (
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-secondary text-secondary-foreground uppercase tracking-wider">
                                                        {(result as DatalabSearchResult).block_type}
                                                    </span>
                                                )}
                                            </>
                                        ) : (
                                            <>
                                                {(result as SearchResult).part && (
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-secondary text-secondary-foreground uppercase tracking-wider">
                                                        Part {(result as SearchResult).part}
                                                    </span>
                                                )}
                                                {(result as SearchResult).question_number && (
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-secondary text-secondary-foreground uppercase tracking-wider">
                                                        Q{(result as SearchResult).question_number}
                                                    </span>
                                                )}
                                                {(result as SearchResult).marks && (
                                                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-secondary text-secondary-foreground uppercase tracking-wider">
                                                        {(result as SearchResult).marks} Marks
                                                    </span>
                                                )}
                                            </>
                                        )}
                                    </div>

                                    {/* Content */}
                                    <p className="text-lg text-foreground/90 leading-relaxed font-serif whitespace-pre-wrap">
                                        {content}
                                    </p>

                                    {/* MCQ Options (Standard only) */}
                                    {!isDatalab && (result as SearchResult).is_mcq && (result as SearchResult).options && (
                                        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
                                            {Object.entries((result as SearchResult).options!).map(([key, value]) => (
                                                <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-border">
                                                    <span className="flex items-center justify-center w-8 h-8 rounded-md bg-primary/10 text-primary font-bold font-mono border border-primary/20">
                                                        {key}
                                                    </span>
                                                    <span className="text-sm text-foreground/80">{value}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )})}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

