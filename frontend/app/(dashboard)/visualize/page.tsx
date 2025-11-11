// app/dashboard/visualize/page.tsx

"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { 
  BarChart, 
  LineChart, 
  PieChart as PieChartIcon,
  Database,
  TrendingUp
} from "lucide-react";
import {
  BarChart as RechartsBar,
  Bar,
  LineChart as RechartsLine,
  Line,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function VisualizePage() {
  const { toast } = useToast();
  const { datasets, currentDataset, setCurrentDataset } = useStore();
  
  const [datasetPreview, setDatasetPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedXAxis, setSelectedXAxis] = useState("");
  const [selectedYAxis, setSelectedYAxis] = useState("");

  useEffect(() => {
    if (datasets.length > 0 && !currentDataset) {
      setCurrentDataset(datasets[0]);
    }
  }, [datasets, currentDataset, setCurrentDataset]);

  useEffect(() => {
    if (currentDataset) {
      loadDataset();
    }
  }, [currentDataset]);

  const loadDataset = async () => {
    if (!currentDataset) return;
    
    setLoading(true);
    try {
      const data = await api.getDataset(currentDataset.id);
      setDatasetPreview(data);
      
      // Auto-select first columns
      if (data.column_names?.length > 0) {
        setSelectedXAxis(data.column_names[0]);
        if (data.column_names.length > 1) {
          setSelectedYAxis(data.column_names[1]);
        }
      }
    } catch (error) {
      toast({
        title: "Error loading dataset",
        description: "Failed to load dataset for visualization",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    if (!datasetPreview?.preview || !selectedXAxis) return [];
    
    // Take first 20 rows for visualization
    return datasetPreview.preview.slice(0, 20).map((row: any) => ({
      name: String(row[selectedXAxis] || 'N/A'),
      value: selectedYAxis ? Number(row[selectedYAxis]) || 0 : 1,
    }));
  };

  const chartData = prepareChartData();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Data Visualization</h1>
        <p className="text-muted-foreground text-lg">
          Visualize your data with interactive charts
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Configuration Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-base">
              <Database className="h-4 w-4 mr-2" />
              Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Dataset</label>
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
            </div>

            {datasetPreview && (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium">X-Axis (Category)</label>
                  <Select value={selectedXAxis} onValueChange={setSelectedXAxis}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {datasetPreview.column_names?.map((col: string) => (
                        <SelectItem key={col} value={col}>
                          {col}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Y-Axis (Value)</label>
                  <Select value={selectedYAxis} onValueChange={setSelectedYAxis}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {datasetPreview.column_names?.map((col: string) => (
                        <SelectItem key={col} value={col}>
                          {col}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    Showing first 20 rows
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Charts Area */}
        <div className="lg:col-span-3">
          <Tabs defaultValue="bar" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="bar">
                <BarChart className="h-4 w-4 mr-2" />
                Bar Chart
              </TabsTrigger>
              <TabsTrigger value="line">
                <LineChart className="h-4 w-4 mr-2" />
                Line Chart
              </TabsTrigger>
              <TabsTrigger value="pie">
                <PieChartIcon className="h-4 w-4 mr-2" />
                Pie Chart
              </TabsTrigger>
            </TabsList>

            <TabsContent value="bar">
              <Card>
                <CardHeader>
                  <CardTitle>Bar Chart</CardTitle>
                  <CardDescription>
                    {selectedXAxis} vs {selectedYAxis || 'Count'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={400}>
                      <RechartsBar data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </RechartsBar>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-96 flex items-center justify-center text-muted-foreground">
                      No data to display
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="line">
              <Card>
                <CardHeader>
                  <CardTitle>Line Chart</CardTitle>
                  <CardDescription>
                    {selectedXAxis} vs {selectedYAxis || 'Count'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={400}>
                      <RechartsLine data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="value" stroke="#3b82f6" />
                      </RechartsLine>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-96 flex items-center justify-center text-muted-foreground">
                      No data to display
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="pie">
              <Card>
                <CardHeader>
                  <CardTitle>Pie Chart</CardTitle>
                  <CardDescription>
                    Distribution of {selectedXAxis}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={400}>
                      <RechartsPie>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => entry.name}
                          outerRadius={120}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </RechartsPie>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-96 flex items-center justify-center text-muted-foreground">
                      No data to display
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}