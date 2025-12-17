import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface Question {
    id: string;
    content: string;
    document_id: string;
    part?: string;
    part_marks?: number;
    question_number?: string;
    unit?: number;
    is_mcq: boolean;
    options?: Record<string, string>;
    correct_answer?: string;
    subject?: string;
    topic?: string;
    difficulty?: string;
    question_type?: string;
    year?: number;
    marks?: number;
    is_mandatory: boolean;
    has_or_option: boolean;
    qdrant_id?: string;
    created_at: string;
    course_code?: string;
    course_name?: string;
    exam_date?: string;
}

export interface Document {
    id: string;
    filename: string;
    file_hash: string;
    page_count?: number;
    course_code?: string;
    course_name?: string;
    semester?: string;
    exam_date?: string;
    total_marks?: number;
    duration_minutes?: number;
    exam_type?: string;
    created_at: string;
}

export interface Job {
    id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    progress: number;
    total_questions: number;
    processed_pages: number;
    error_message?: string;
    created_at: string;
    updated_at: string;
}

export interface SearchResult extends Question {
    score: number;
}

// API Functions
export const uploadFiles = async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const { data } = await api.post<{ job_id: string; status_url: string }>('/api/v1/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};

export const getJobStatus = async (jobId: string) => {
    const { data } = await api.get<Job>(`/api/v1/jobs/${jobId}`);
    return data;
};

export const searchQuestions = async (query: string, limit = 20) => {
    const { data } = await api.get<{ results: SearchResult[] }>('/api/v1/search', {
        params: { q: query, limit },
    });
    return data.results;
};

export const getAllQuestions = async (params?: {
    search?: string;
    course_code?: string;
    year?: string;
    exam_type?: string;
}) => {
    const { data } = await api.get<Question[]>('/api/v1/questions', { params });
    return data;
};

export const getAllDocuments = async () => {
    const { data } = await api.get<Document[]>('/api/v1/documents');
    return data;
};

export const checkHealth = async () => {
    const { data } = await api.get('/health');
    return data;
};
