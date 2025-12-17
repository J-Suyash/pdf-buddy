import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getDocumentDetails, getDocumentPdfUrl } from '../api/client';
import { 
    ArrowLeft, 
    FileText, 
    Calendar, 
    Clock, 
    Award, 
    BookOpen,
    Download,
    Bookmark,
    BookmarkCheck
} from 'lucide-react';
import { cn } from '../utils';

export default function QuestionPaper() {
    const { documentId } = useParams<{ documentId: string }>();
    const navigate = useNavigate();
    const [selectedPart, setSelectedPart] = useState<string>('all');
    const [markedQuestions, setMarkedQuestions] = useState<Set<string>>(new Set());

    const { data: document, isLoading, error } = useQuery({
        queryKey: ['document', documentId],
        queryFn: () => getDocumentDetails(documentId!),
        enabled: !!documentId,
    });

    // Load marked questions from localStorage
    useEffect(() => {
        if (documentId) {
            const stored = localStorage.getItem(`marked_${documentId}`);
            if (stored) {
                setMarkedQuestions(new Set(JSON.parse(stored)));
            }
        }
    }, [documentId]);

    // Save marked questions to localStorage
    const toggleMarkQuestion = (questionId: string) => {
        setMarkedQuestions(prev => {
            const newSet = new Set(prev);
            if (newSet.has(questionId)) {
                newSet.delete(questionId);
            } else {
                newSet.add(questionId);
            }
            // Save to localStorage
            localStorage.setItem(`marked_${documentId}`, JSON.stringify([...newSet]));
            return newSet;
        });
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            </div>
        );
    }

    if (error || !document) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
                <FileText className="w-16 h-16 text-muted-foreground" />
                <h2 className="text-2xl font-bold text-foreground">Document not found</h2>
                <button
                    onClick={() => navigate('/library')}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
                >
                    Back to Library
                </button>
            </div>
        );
    }

    // Group questions by part
    const questionsByPart = (document.questions || []).reduce((acc, q) => {
        const part = q.part || 'Other';
        if (!acc[part]) acc[part] = [];
        acc[part].push(q);
        return acc;
    }, {} as Record<string, typeof document.questions>);

    // Sort questions within each part
    Object.keys(questionsByPart).forEach(part => {
        questionsByPart[part].sort((a, b) => {
            const numA = parseInt(a.question_number || '0');
            const numB = parseInt(b.question_number || '0');
            return numA - numB;
        });
    });

    // Filter questions based on selected part
    const filteredQuestions = selectedPart === 'all' 
        ? Object.values(questionsByPart).flat()
        : questionsByPart[selectedPart] || [];

    // Count marked questions
    const markedCount = filteredQuestions.filter(q => markedQuestions.has(q.id)).length;

    const pdfUrl = getDocumentPdfUrl(documentId!);
    const parts = ['all', ...Object.keys(questionsByPart).sort()];

    return (
        <div className="max-w-7xl mx-auto pt-6 space-y-6 pb-12">
            {/* Header */}
            <div className="flex items-start justify-between animate-fade-in">
                <div className="flex-1">
                    <button
                        onClick={() => navigate('/library')}
                        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span className="text-sm font-medium">Back to Library</span>
                    </button>
                    
                    <div className="flex items-start gap-4 mb-4">
                        <div className="p-3 rounded-xl bg-primary/10 text-primary">
                            <FileText className="w-8 h-8" />
                        </div>
                        <div className="flex-1">
                            <h1 className="text-3xl font-heading font-bold text-foreground mb-2">
                                {document.course_code || 'Question Paper'}
                            </h1>
                            <p className="text-lg text-muted-foreground">
                                {document.course_name || document.filename}
                            </p>
                        </div>
                    </div>

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-3">
                        {document.semester && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">
                                <BookOpen className="w-4 h-4" />
                                {document.semester}
                            </div>
                        )}
                        {document.exam_date && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">
                                <Calendar className="w-4 h-4" />
                                {document.exam_date}
                            </div>
                        )}
                        {document.duration_minutes && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">
                                <Clock className="w-4 h-4" />
                                {document.duration_minutes} mins
                            </div>
                        )}
                        {document.total_marks && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm font-medium">
                                <Award className="w-4 h-4" />
                                {document.total_marks} marks
                            </div>
                        )}
                        {markedCount > 0 && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 text-sm font-medium">
                                <BookmarkCheck className="w-4 h-4" />
                                {markedCount} marked for review
                            </div>
                        )}
                    </div>
                </div>

                <a
                    href={pdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
                >
                    <Download className="w-4 h-4" />
                    Download PDF
                </a>
            </div>

            {/* Part Filter Dropdown */}
            <div className="flex items-center gap-4 animate-slide-up">
                <label htmlFor="part-filter" className="text-sm font-medium text-foreground">
                    Filter by Part:
                </label>
                <select
                    id="part-filter"
                    value={selectedPart}
                    onChange={(e) => setSelectedPart(e.target.value)}
                    className="px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-foreground"
                >
                    {parts.map(part => (
                        <option key={part} value={part}>
                            {part === 'all' ? 'All Parts' : `Part ${part}`}
                            {part !== 'all' && questionsByPart[part] ? ` (${questionsByPart[part].length})` : ''}
                        </option>
                    ))}
                </select>
            </div>

            {/* Main Content - Split View */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Questions List */}
                <div className="space-y-4 animate-slide-up">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold font-heading text-foreground">
                            Questions {selectedPart !== 'all' && `- Part ${selectedPart}`}
                        </h2>
                        <span className="text-sm text-muted-foreground">
                            {filteredQuestions.length} question{filteredQuestions.length !== 1 ? 's' : ''}
                        </span>
                    </div>
                    
                    <div className="space-y-3">
                        {filteredQuestions.map((question) => {
                            const isMarked = markedQuestions.has(question.id);
                            return (
                                <div 
                                    key={question.id} 
                                    className={cn(
                                        "rounded-xl border bg-card p-4 transition-all hover:shadow-md",
                                        isMarked ? "border-orange-500 bg-orange-50 dark:bg-orange-900/10" : "border-border"
                                    )}
                                >
                                    <div className="flex items-start gap-3 mb-3">
                                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-secondary text-secondary-foreground font-bold text-sm font-mono flex-shrink-0">
                                            {question.question_number}
                                        </span>
                                        <div className="flex-1">
                                            <p className="text-foreground font-serif leading-relaxed">
                                                {question.content}
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => toggleMarkQuestion(question.id)}
                                            className={cn(
                                                "p-2 rounded-lg transition-colors flex-shrink-0",
                                                isMarked 
                                                    ? "bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400" 
                                                    : "hover:bg-muted text-muted-foreground hover:text-foreground"
                                            )}
                                            title={isMarked ? "Remove review mark" : "Mark for review"}
                                        >
                                            {isMarked ? <BookmarkCheck className="w-5 h-5" /> : <Bookmark className="w-5 h-5" />}
                                        </button>
                                    </div>

                                    {question.is_mcq && question.options && (
                                        <div className="ml-11 space-y-2 mt-3">
                                            {Object.entries(question.options).map(([key, value]) => (
                                                <div key={key} className="flex gap-3 items-start">
                                                    <span className="w-6 h-6 rounded flex items-center justify-center bg-muted text-muted-foreground text-xs font-bold flex-shrink-0">
                                                        {key}
                                                    </span>
                                                    <span className="text-sm text-foreground/80">{value}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    <div className="ml-11 mt-3 flex flex-wrap gap-2">
                                        {question.part && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-muted text-muted-foreground">
                                                Part {question.part}
                                            </span>
                                        )}
                                        {question.unit && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-muted text-muted-foreground">
                                                Unit {question.unit}
                                            </span>
                                        )}
                                        {question.marks && (
                                            <span className="px-2 py-0.5 rounded text-xs font-bold bg-primary/10 text-primary">
                                                {question.marks} mark{question.marks !== 1 ? 's' : ''}
                                            </span>
                                        )}
                                        {question.is_mcq && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                                                MCQ
                                            </span>
                                        )}
                                        {question.has_or_option && (
                                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                                                OR
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}

                        {filteredQuestions.length === 0 && (
                            <div className="text-center py-12 text-muted-foreground">
                                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                <p>No questions found for the selected filter.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* PDF Preview */}
                <div className="lg:sticky lg:top-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
                    <div className="rounded-xl border border-border bg-card overflow-hidden">
                        <div className="p-4 border-b border-border bg-muted/50">
                            <h2 className="text-lg font-bold font-heading text-foreground">PDF Preview</h2>
                        </div>
                        <div className="bg-muted/20">
                            <iframe
                                src={pdfUrl}
                                className="w-full h-[calc(100vh-12rem)] border-0"
                                title="PDF Preview"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
