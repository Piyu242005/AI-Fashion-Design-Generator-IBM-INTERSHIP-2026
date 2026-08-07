/**
 * hooks/useDocuments.ts — Document management hook
 * ==================================================
 * Upload, list, and delete study documents.
 * Automatically refetches list after upload/delete.
 */

"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { documentsApi } from "@/services/api";
import type { Document } from "@/types";

export function useDocuments() {
  const qc = useQueryClient();

  // List documents
  const { data: documents = [], isLoading } = useQuery<Document[]>({
    queryKey: ["documents"],
    queryFn: async () => {
      const res = await documentsApi.list();
      return res.data;
    },
  });

  // Upload document
  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentsApi.upload(file),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success(`"${res.data.filename}" uploaded successfully!`);
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail ?? "Upload failed.";
      toast.error(msg);
    },
  });

  // Delete document
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Document deleted.");
    },
    onError: () => toast.error("Failed to delete document."),
  });

  return {
    documents,
    isLoading,
    upload: uploadMutation.mutateAsync,
    deleteDoc: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
