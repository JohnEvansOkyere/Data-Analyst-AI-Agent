// app/dashboard/analysis/page.tsx


"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { 
  BrainCircuit, 
  Loader2, 
  Database, 
  Code, 
  Lightbulb,
  Download,
  Settings
} from "lucide-react";
import { formatNumber } from "@/lib/utils";

const AI_PROVIDERS = [
  { value: "xai", label: "xAI Grok", models: ["grok-2-1212", "grok-beta"] },
  { value: "groq", label: "Groq", models: ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"] },
  { value: "gemini", label: "Google Gemini", models: ["gemini-1.5-flash", "gemini-1.5-pro"] },
];

export default function AnalysisPage() {
  const { toast } = useToast();
  const { datasets, currentDataset, setCurrentDataset } = useStore();

  // AI Configuration State
  const [aiConfigured, setAiConfigured] = useState(false);
  const [provider, setProvider] = useState("xai");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("");
  const [configuringAI, setConfiguringAI] = useState(false);

  // Query State
  const [query, setQuery] = useState("");
  const [querying, setQuerying] = useState(false);
  const [queryResult, setQueryResult] = useState<any>(null);

  // Dataset Preview State
  const [datasetPreview, setDatasetPreview] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);

  useEffect(() => {
    if (datasets.length > 0 && !currentDataset) {
      setCurrentDataset(datasets[0]);
    }
  }, [datasets, currentDataset, setCurrentDataset]);

  useEffect(() => {
    if (currentDataset) {
      loadDatasetPreview();
    }
  }, [currentDataset]);

  const loadDatasetPreview = async () => {
    if (!currentDataset) return;
    
    setLoadingPreview(true);
    try {
      const preview = await api.getDataset(currentDataset.id);
      setDatasetPreview(preview);
    } catch (error) {
      toast({
        title: "Error loading preview",
        description: "Failed to load dataset preview",
        variant: "destructive",
      });
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleConfigureAI = async () => {
    if (!apiKey || !model) {
      toast({
        title: "Missing information",
        description: "Please select a model and enter your API key",
        variant: "destructive",
      });
      return;
    }

    setConfiguringAI(true);

    try {
      await api.configureAI(provider, apiKey, model);
      setAiConfigured(true);
      toast({
        title: "AI Configured!",
        description: `Using ${AI_PROVIDERS.find(p => p.value === provider)?.label} with ${model}`,
      });
    } catch (error: any) {
      toast({
        title: "Configuration failed",
        description: error.response?.data?.detail || "Failed to configure AI",
        variant: "destructive",
      });
    } finally {
      setConfiguringAI(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      toast({
        title: "Empty query",
        description: "Please enter a question",
        variant: "destructive",
      });
      return;
    }

    if (!currentDataset) {
      toast({
        title: "No dataset selected",
        description: "Please select a dataset first",
        variant: "destructive",
      });
      return;
    }

    if (!aiConfigured) {
      toast({
        title: "AI not configured",
        description: "Please configure AI provider first",
        variant: "destructive",
      });
      return;
    }

    setQuerying(true);
    setQueryResult(null);

    try {
      const result = await api.queryAI(query, currentDataset.id);
      setQueryResult(result);
      toast({
        title: "Query completed!",
        description: `Found ${result.rows} result${result.rows !== 1 ? 's' : ''}`,
      });
    } catch (error: any) {
      toast({
        title: "Query failed",
        description: error.response?.data?.detail || "Failed to execute query",
        variant: "destructive",
      });
    } finally {
      setQuerying(false);
    }
  };

  const downloadResults = () => {
    if (!queryResult?.results) return;

    const csv = [
      Object.keys(queryResult.results[0]).join(','),
      ...queryResult.results.map((row: any) => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query_results_${Date.now()}.csv`;
    a.click();
  };

  const quickQuestions = [
    "What are the top 10 records?",
    "Show me summary statistics",
    "What is the distribution by category?",
    "Find any outliers in the data",
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">AI Analysis</h1>
        <p className="text-muted-foreground text-lg">
          Ask questions about your data in natural language
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Configuration & Dataset */}
        <div className="space-y-6">
          {/* Dataset Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <Database className="h-4 w-4 mr-2" />
                Select Dataset
              </CardTitle>
            </CardHeader>
            <CardContent>
              {datasets.length === 0 ? (
                <p className="text-sm text-muted-foreground">No datasets available</p>
              ) : (
                <Select
                  value={currentDataset?.id}
                  onValueChange={(value) => {
                    const dataset = datasets.find((d: any) => d.id === value);
                    setCurrentDataset(dataset);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select dataset" />
                  </SelectTrigger>
                  <SelectContent>
                    {datasets.map((dataset: any) => (
                      <SelectItem key={dataset.id} value={dataset.id}>
                        {dataset.dataset_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {currentDataset && (
                <div className="mt-4 p-3 bg-secondary/50 rounded-lg space-y-1 text-sm">
                  <p className="font-medium">{currentDataset.dataset_name}</p>
                  <p className="text-muted-foreground">
                    {formatNumber(currentDataset.row_count)} rows × {currentDataset.column_count} columns
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-base">
                <Settings className="h-4 w-4 mr-2" />
                AI Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Provider</Label>
                <Select value={provider} onValueChange={(value) => {
                  setProvider(value);
                  setModel("");
                }}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {AI_PROVIDERS.map((p) => (
                      <SelectItem key={p.value} value={p.value}>
                        {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Model</Label>
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {AI_PROVIDERS.find(p => p.value === provider)?.models.map((m) => (
                      <SelectItem key={m} value={m}>
                        {m}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>API Key</Label>
                <Input
                  type="password"
                  placeholder="Enter API key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>

              <Button
                onClick={handleConfigureAI}
                disabled={configuringAI || !apiKey || !model}
                className="w-full"
              >
                {configuringAI ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Configuring...
                  </>
                ) : aiConfigured ? (
                  "✓ Configured"
                ) : (
                  "Configure AI"
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Dataset Preview */}
          {datasetPreview && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Available Columns</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1 max-h-60 overflow-y-auto">
                  {datasetPreview.column_names?.map((col: string, idx: number) => (
                    <div key={idx} className="text-sm py-1 px-2 bg-secondary/30 rounded">
                      {col}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Query Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Query Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BrainCircuit className="h-5 w-5 mr-2" />
                Ask a Question
              </CardTitle>
              <CardDescription>
                Type your question in plain English
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="e.g., What is the most used PreferredLoginDevice by Gender?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={4}
                disabled={querying}
              />

              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((q, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => setQuery(q)}
                    disabled={querying}
                  >
                    {q}
                  </Button>
                ))}
              </div>

              <Button
                onClick={handleQuery}
                disabled={querying || !aiConfigured || !currentDataset || !query.trim()}
                className="w-full"
                size="lg"
              >
                {querying ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="mr-2 h-4 w-4" />
                    Analyze with AI
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Query Results */}
          {queryResult && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Query Results</CardTitle>
                  <Button variant="outline" size="sm" onClick={downloadResults}>
                    <Download className="h-4 w-4 mr-2" />
                    Download CSV
                  </Button>
                </div>
                <CardDescription>
                  {queryResult.rows} row{queryResult.rows !== 1 ? 's' : ''} × {queryResult.columns} column{queryResult.columns !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="results">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="results">Results</TabsTrigger>
                    <TabsTrigger value="sql">Generated SQL</TabsTrigger>
                    <TabsTrigger value="insights">AI Insights</TabsTrigger>
                  </TabsList>

                  <TabsContent value="results" className="space-y-4">
                    <div className="border rounded-lg overflow-hidden">
                      <div className="overflow-x-auto max-h-96">
                        <table className="w-full text-sm">
                          <thead className="bg-secondary">
                            <tr>
                              {queryResult.results[0] && Object.keys(queryResult.results[0]).map((key: string) => (
                                <th key={key} className="px-4 py-2 text-left font-medium">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {queryResult.results.map((row: any, idx: number) => (
                              <tr key={idx} className="border-t hover:bg-accent/50">
                                {Object.values(row).map((value: any, vidx: number) => (
                                  <td key={vidx} className="px-4 py-2">
                                    {value === null ? (
                                      <span className="text-muted-foreground italic">null</span>
                                    ) : (
                                      String(value)
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="sql">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center text-base">
                          <Code className="h-4 w-4 mr-2" />
                          Generated SQL Query
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <pre className="p-4 bg-secondary rounded-lg overflow-x-auto text-sm">
                          <code>{queryResult.sql}</code>
                        </pre>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="insights">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center text-base">
                          <Lightbulb className="h-4 w-4 mr-2" />
                          AI Interpretation
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="prose prose-sm max-w-none">
                          <p className="whitespace-pre-wrap">{queryResult.interpretation}</p>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}