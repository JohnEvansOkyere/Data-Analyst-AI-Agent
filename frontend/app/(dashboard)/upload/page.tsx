
// app/dashboard/upload/page.tsx

"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { Upload, FileText, CheckCircle, Loader2, Database } from "lucide-react";
import { formatNumber, formatDate } from "@/lib/utils";

export default function UploadPage() {
  const { toast } = useToast();
  const { datasets, setDatasets } = useStore();
  const [file, setFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      
      // Auto-generate dataset name from filename
      if (!datasetName) {
        const name = selectedFile.name.replace(/\.(csv|xlsx?)$/i, '');
        setDatasetName(name);
      }
    }
  };

  const handleUpload = async () => {
    if (!file || !datasetName) {
      toast({
        title: "Missing information",
        description: "Please select a file and enter a dataset name",
        variant: "destructive",
      });
      return;
    }

    // Validate file type
    const validTypes = ['.csv', '.xlsx', '.xls'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!validTypes.includes(fileExt)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a CSV or Excel file",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (200MB limit)
    const maxSize = 200 * 1024 * 1024; // 200MB
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "Maximum file size is 200MB",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);
    setUploadSuccess(false);

    try {
      const response = await api.uploadDataset(file, datasetName);

      if (response.success) {
        setUploadSuccess(true);
        toast({
          title: "Upload successful!",
          description: `${response.dataset.name} uploaded with ${formatNumber(response.dataset.rows)} rows`,
        });

        // Refresh datasets list
        const datasetsResponse = await api.getDatasets();
        setDatasets(datasetsResponse.datasets);

        // Reset form
        setTimeout(() => {
          setFile(null);
          setDatasetName("");
          setUploadSuccess(false);
        }, 3000);
      }
    } catch (error: any) {
      toast({
        title: "Upload failed",
        description: error.response?.data?.detail || "Failed to upload dataset",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Upload Dataset</h1>
        <p className="text-muted-foreground text-lg">
          Upload your CSV or Excel files to start analyzing
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Form */}
        <Card>
          <CardHeader>
            <CardTitle>Upload New Dataset</CardTitle>
            <CardDescription>
              Supported formats: CSV, Excel (.xlsx, .xls)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dataset-name">Dataset Name</Label>
              <Input
                id="dataset-name"
                placeholder="e.g., Customer Sales Q1 2024"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                disabled={uploading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="file-upload">Select File</Label>
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
                {file ? (
                  <div className="space-y-2">
                    <FileText className="h-12 w-12 text-primary mx-auto" />
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFile(null)}
                      disabled={uploading}
                    >
                      Change File
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
                    <p className="text-sm text-muted-foreground">
                      Click to browse or drag and drop
                    </p>
                    <Input
                      id="file-upload"
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileChange}
                      className="hidden"
                      disabled={uploading}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => document.getElementById('file-upload')?.click()}
                      disabled={uploading}
                    >
                      Browse Files
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {uploadSuccess && (
              <div className="flex items-center space-x-2 text-green-600 bg-green-50 dark:bg-green-950/20 p-3 rounded-lg">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">Upload successful!</span>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!file || !datasetName || uploading}
              className="w-full"
              size="lg"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Dataset
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Upload Guidelines */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Guidelines</CardTitle>
            <CardDescription>Tips for best results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="font-medium">File Format</p>
                  <p className="text-sm text-muted-foreground">
                    CSV (.csv) or Excel (.xlsx, .xls) formats supported
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="font-medium">File Size</p>
                  <p className="text-sm text-muted-foreground">
                    Maximum 200MB per file
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="font-medium">Data Structure</p>
                  <p className="text-sm text-muted-foreground">
                    First row should contain column headers
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="font-medium">Data Quality</p>
                  <p className="text-sm text-muted-foreground">
                    Missing values are automatically handled
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <p className="font-medium">Security</p>
                  <p className="text-sm text-muted-foreground">
                    All data is encrypted and stored securely
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
              <p className="text-sm font-medium mb-2">💡 Pro Tip</p>
              <p className="text-sm text-muted-foreground">
                Clean column names (no special characters) will give better results with AI queries
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Existing Datasets */}
      <Card>
        <CardHeader>
          <CardTitle>Your Datasets</CardTitle>
          <CardDescription>
            {datasets.length} dataset{datasets.length !== 1 ? 's' : ''} uploaded
          </CardDescription>
        </CardHeader>
        <CardContent>
          {datasets.length === 0 ? (
            <div className="text-center py-12">
              <Database className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No datasets uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {datasets.map((dataset: any) => (
                <div
                  key={dataset.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-primary/10 rounded">
                      <Database className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{dataset.dataset_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatNumber(dataset.row_count)} rows × {dataset.column_count} columns • {(dataset.file_size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground mb-2">
                      {formatDate(dataset.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}