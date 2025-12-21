import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { uploadFiles, uploadDatalabFile, getJobStatus } from '../api/client';
import { Upload as UploadIcon, X, CheckCircle2, FileText, Loader2, Zap, BrainCircuit, FileStack } from 'lucide-react';
import { cn } from '../utils';

export default function Upload() {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [jobId, setJobId] = useState<string | null>(null);
    const [uploadType, setUploadType] = useState<'datalab' | 'pdf'>('datalab');

    const uploadMutation = useMutation({
        mutationFn: async (files: File[]) => {
            if (uploadType === 'datalab') {
                return uploadDatalabFile(files[0]);
            }
            return uploadFiles(files);
        },
        onSuccess: (data) => {
            setJobId(data.job_id);
            setSelectedFiles([]);
        },
    });

    const { data: jobStatus } = useQuery({
        queryKey: ['job', jobId],
        queryFn: () => getJobStatus(jobId!),
        enabled: !!jobId,
        refetchInterval: (query) => {
            const data = query.state.data;
            if (!data) return false;
            return data.status === 'processing' || data.status === 'queued' ? 2000 : false;
        },
    });

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (uploadType === 'datalab') {
            setSelectedFiles(files.slice(0, 1));
        } else {
            setSelectedFiles(prev => [...prev, ...files].slice(0, 10));
        }
    };

    const handleUpload = () => {
        if (selectedFiles.length > 0) {
            uploadMutation.mutate(selectedFiles);
        }
    };

    return (
        <div className="space-y-12 max-w-4xl mx-auto pt-10">
            {/* Header */}
            <div className="text-center space-y-4">
                 <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm font-medium mb-4 animate-fade-in">
                    <Zap className="w-4 h-4" />
                    <span>Fast Extraction Engine</span>
                </div>
                <h1 className="text-5xl font-heading font-bold tracking-tight mb-4 text-foreground">
                    Upload & Process
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Transform your PDF question papers into searchable data.
                </p>
            </div>

            <div className="flex justify-center">
                <div className="bg-card border border-border p-1 rounded-xl inline-flex shadow-sm">
                    <button
                        className={cn(
                            "px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                            uploadType === 'datalab'
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground hover:bg-muted"
                        )}
                        onClick={() => {
                            setUploadType('datalab');
                            setSelectedFiles([]);
                            setJobId(null);
                        }}
                    >
                        <BrainCircuit className="w-4 h-4" />
                        DataLab (Enhanced OCR)
                    </button>
                    <button
                        className={cn(
                            "px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                            uploadType === 'pdf'
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground hover:bg-muted"
                        )}
                        onClick={() => {
                            setUploadType('pdf');
                            setSelectedFiles([]);
                            setJobId(null);
                        }}
                    >
                        <FileStack className="w-4 h-4" />
                        Standard PDF
                    </button>
                </div>
            </div>

            <div className="grid gap-8">
                {/* Upload Zone */}
                <div className="group relative rounded-2xl border-2 border-dashed border-muted-foreground/20 hover:border-primary transition-all duration-300 bg-card hover:bg-muted/50">
                    <input
                        type="file"
                        accept=".pdf"
                        multiple={uploadType === 'pdf'}
                        onChange={handleFileSelect}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                        id="file-upload"
                    />
                    <div className="p-16 text-center space-y-4 transition-transform group-hover:scale-105 duration-300">
                        <div className="w-20 h-20 mx-auto rounded-full bg-muted flex items-center justify-center mb-6 group-hover:bg-primary/10 transition-colors">
                            <UploadIcon className="w-10 h-10 text-muted-foreground group-hover:text-primary" />
                        </div>
                        <h3 className="text-2xl font-bold font-heading text-foreground">
                            {uploadType === 'datalab' ? 'Drop single PDF here' : 'Drop PDFs here'}
                        </h3>
                        <p className="text-muted-foreground max-w-sm mx-auto">
                            {uploadType === 'datalab' 
                                ? 'Enhanced processing for complex documents. 1 file limit.' 
                                : 'Support for scanned and digital PDFs. Up to 10 files at once.'}
                        </p>
                    </div>
                </div>

                {/* Selected Files List */}
                {selectedFiles.length > 0 && (
                    <div className="space-y-4 animate-slide-up">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-foreground">Selected Files</h3>
                            <span className="text-sm text-muted-foreground">{selectedFiles.length} files ready</span>
                        </div>
                        <div className="grid gap-3">
                            {selectedFiles.map((file, idx) => (
                                <div key={idx} className="flex items-center justify-between p-4 bg-card border border-border rounded-xl">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center border border-border">
                                            <FileText className="w-5 h-5 text-muted-foreground" />
                                        </div>
                                        <div>
                                            <p className="font-medium truncate max-w-[300px] text-foreground">{file.name}</p>
                                            <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== idx))}
                                        className="p-2 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-colors text-muted-foreground"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}
                        </div>
                        <button
                            onClick={handleUpload}
                            disabled={uploadMutation.isPending}
                            className="w-full py-4 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all font-bold text-lg flex items-center justify-center gap-2"
                        >
                            {uploadMutation.isPending ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" /> Uploading...
                                </>
                            ) : (
                                'Start Processing'
                            )}
                        </button>
                    </div>
                )}


                {/* Status Card */}
                {jobStatus && (
                    <div className="rounded-2xl bg-card border border-border p-8 space-y-8 animate-fade-in shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-xl font-bold font-heading mb-1 text-foreground">Job Status</h3>
                                <p className="text-sm text-muted-foreground font-mono">{jobStatus.id}</p>
                            </div>
                            <span className={cn(
                                "px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider",
                                jobStatus.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                                jobStatus.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                                'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 animate-pulse'
                            )}>
                                {jobStatus.status}
                            </span>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm font-medium text-foreground">
                                <span>Progress</span>
                                <span>{jobStatus.progress}%</span>
                            </div>
                            <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                                <div
                                    className="bg-primary h-full rounded-full transition-all duration-500 relative"
                                    style={{ width: `${jobStatus.progress}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]" />
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-6 bg-muted/30 rounded-xl border border-border text-center">
                                <p className="text-sm text-muted-foreground mb-1 uppercase tracking-wide">
                                    {uploadType === 'datalab' ? 'Chunks Extracted' : 'Questions Extracted'}
                                </p>
                                <p className="text-4xl font-bold font-heading text-primary">{jobStatus.total_questions}</p>
                            </div>
                            <div className="p-6 bg-muted/30 rounded-xl border border-border text-center">
                                <p className="text-sm text-muted-foreground mb-1 uppercase tracking-wide">Pages Processed</p>
                                <p className="text-4xl font-bold font-heading text-foreground">{jobStatus.processed_pages}</p>
                            </div>
                        </div>

                        {jobStatus.status === 'completed' && (
                            <div className="flex items-center justify-center gap-3 p-4 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-xl">
                                <CheckCircle2 className="w-6 h-6" />
                                <span className="font-semibold">Processing completed successfully!</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
