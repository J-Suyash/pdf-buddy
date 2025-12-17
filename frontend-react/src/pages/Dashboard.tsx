import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getAllQuestions, getAllDocuments } from '../api/client';
import { Library, FileText, CheckCircle, FileQuestion, ArrowUpRight, Clock } from 'lucide-react';
import { cn } from '../utils';

interface StatCardProps {
    title: string;
    value: number;
    icon: React.ElementType;
    colorClass: string;
    delay: number;
}

function StatCard({ title, value, icon: Icon, colorClass, delay }: StatCardProps) {
    return (
        <div 
            className="group relative overflow-hidden rounded-2xl bg-card border border-border p-6 transition-all duration-300 hover:border-primary/50 hover:shadow-lg animate-slide-up"
            style={{ animationDelay: `${delay}ms` }}
        >
            <div className="relative z-10">
                <div className="flex items-center justify-between mb-8">
                    <div className={cn("p-3 rounded-xl bg-muted group-hover:bg-primary/10 transition-colors duration-300 text-foreground group-hover:text-primary")}>
                        <Icon className="w-6 h-6" />
                    </div>
                    <span className="flex items-center text-xs font-medium text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
                        +12% <ArrowUpRight className="w-3 h-3 ml-1" />
                    </span>
                </div>
                
                <div className="space-y-1">
                    <h3 className="text-4xl font-bold font-heading tracking-tight text-foreground">{value.toLocaleString()}</h3>
                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">{title}</p>
                </div>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const navigate = useNavigate();
    const { data: questions = [], isLoading: questionsLoading } = useQuery({
        queryKey: ['questions'],
        queryFn: () => getAllQuestions(),
    });

    const { data: documents = [], isLoading: documentsLoading } = useQuery({
        queryKey: ['documents'],
        queryFn: getAllDocuments,
    });

    const isLoading = questionsLoading || documentsLoading;

    const stats = [
        {
            title: 'Total Questions',
            value: questions.length,
            icon: Library,
            colorClass: 'text-blue-500',
        },
        {
            title: 'Documents',
            value: documents.length,
            icon: FileText,
            colorClass: 'text-purple-500',
        },
        {
            title: 'MCQs',
            value: questions.filter(q => q.is_mcq).length,
            icon: CheckCircle,
            colorClass: 'text-green-500',
        },
        {
            title: 'Descriptive',
            value: questions.filter(q => !q.is_mcq).length,
            icon: FileQuestion,
            colorClass: 'text-orange-500',
        },
    ];

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-10 pt-6">
            <div className="flex items-end justify-between animate-fade-in">
                <div>
                    <h1 className="text-4xl font-heading font-bold text-foreground mb-2">
                        Welcome back, <span className="text-primary">Scholar</span>
                    </h1>
                    <p className="text-muted-foreground text-lg">
                        Here's what's happening in your digital library today.
                    </p>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground bg-card px-4 py-2 rounded-full border border-border">
                    <Clock className="w-4 h-4" />
                    <span>Last updated: Just now</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <StatCard key={stat.title} {...stat} delay={index * 100} />
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity / Chart Placeholder */}
                <div className="lg:col-span-2 rounded-2xl bg-card border border-border p-8 min-h-[400px] animate-slide-up" style={{ animationDelay: '400ms' }}>
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xl font-bold font-heading text-foreground">Ingestion Activity</h2>
                        <select className="bg-background border border-border rounded-lg px-3 py-1 text-sm outline-none focus:border-primary text-foreground">
                            <option>Last 7 Days</option>
                            <option>Last 30 Days</option>
                        </select>
                    </div>
                    
                    {/* Fake Chart Visualization */}
                    <div className="h-64 flex items-end justify-between gap-2 px-4">
                        {[40, 65, 30, 85, 50, 95, 75].map((height, i) => (
                            <div key={i} className="w-full bg-muted/30 rounded-t-lg relative group h-full">
                                <div 
                                    className="absolute bottom-0 left-0 right-0 bg-primary/20 hover:bg-primary/40 transition-all duration-500 rounded-t-lg"
                                    style={{ height: `${height}%` }}
                                >
                                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-full opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold mb-2 bg-popover text-popover-foreground px-2 py-1 rounded shadow-lg whitespace-nowrap z-20">
                                        {height} docs
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 text-xs text-muted-foreground font-mono uppercase">
                        <span>Mon</span>
                        <span>Tue</span>
                        <span>Wed</span>
                        <span>Thu</span>
                        <span>Fri</span>
                        <span>Sat</span>
                        <span>Sun</span>
                    </div>
                </div>

                {/* Quick Actions or Recent Files */}
                <div className="rounded-2xl bg-card border border-border p-8 animate-slide-up" style={{ animationDelay: '500ms' }}>
                    <h2 className="text-xl font-bold font-heading mb-6 text-foreground">Recent Documents</h2>
                    <div className="space-y-4">
                        {documents.slice(0, 5).map((doc, i) => (
                            <div 
                                key={doc.id} 
                                onClick={() => navigate(`/paper/${doc.id}`)}
                                className="flex items-center gap-4 p-3 rounded-xl hover:bg-muted/50 transition-colors cursor-pointer group"
                            >
                                <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
                                    <FileText className="w-5 h-5" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium truncate text-sm text-foreground">{doc.filename}</p>
                                    <p className="text-xs text-muted-foreground">{new Date(doc.created_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                        ))}
                        {documents.length === 0 && (
                            <p className="text-muted-foreground text-sm text-center py-8">No documents uploaded yet.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
