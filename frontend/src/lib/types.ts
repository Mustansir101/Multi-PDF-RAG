export type BackendProcessResponse = {
  message: string;
  session_id: string;
  files: string[];
};

export type BackendAskResponse = {
  answer: string;
  sources?: SourceRef[];
};

export type ProcessResult = {
  files: string[];
  sessionId: string;
  message?: string;
};

export type SourceRef = {
  source: string;
  page_label: number;
};

export type ChatResponse = {
  answer: string;
  sources?: SourceRef[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: number;
  sources?: SourceRef[];
};
