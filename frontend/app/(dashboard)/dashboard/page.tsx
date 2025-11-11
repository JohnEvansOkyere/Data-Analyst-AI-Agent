// app/dashboard/page.tsx


"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { useToast } from "@/components/ui/use-toast";
import { 
  Database, 
  TrendingUp, 
  Activity, 
  Upload,
  ArrowRight,
  CheckCircle
} from "lucide-react";
import Link from "next/link";
import { formatDate, formatNumber } from "@/lib/utils";

export default function DashboardPage() {
  const { user, datasets, setDatasets } = useStore();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDatasets: 0,
    totalRows: 0,
    totalColumns: 0,
    lastUpload: null as string | null,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await api.getDatasets();
      const datasetList = response.datasets || [];
      setDatasets(datasetList);

      // Calculate stats
      const totalRows = datasetList.reduce((sum: number, ds: any) => sum + (ds.row_count || 0), 0);
      const totalColumns = datasetList.reduce((sum: number, ds: any) => sum + (ds.column_count || 0), 0);
      const lastUpload = datasetList.length > 0 ? datasetList[0].created_at : null;

      setStats({
        totalDatasets: datasetList.length,
        totalRows,
        totalColumns,
        lastUpload,
      });
    } catch (error) {
      toast({
        title: "Error loading dashboard",
        description: "Failed to load dashboard data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">
          Welcome back, {user?.full_name?.split(' ')[0] || user?.username}! 👋
        </h1>
        <p className="text-muted-foreground text-lg">
          Here's what's happening with your data today
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Datasets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalDatasets)}</div>
            <p className="text-xs text-muted-foreground">
              {stats.lastUpload ? `Last upload ${formatDate(stats.lastUpload)}` : "No uploads yet"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Rows</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalRows)}</div>
            <p className="text-xs text-muted-foreground">
              Across all datasets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Columns</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.totalColumns)}</div>
            <p className="text-xs text-muted-foreground">
              Total features tracked
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Active</div>
            <p className="text-xs text-muted-foreground">
              All systems operational
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with your data analysis</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <Link href="/upload">
            <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center space-y-2">
              <Upload className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Upload Dataset</span>
            </Button>
          </Link>

          <Link href="/analysis">
            <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center space-y-2">
              <Activity className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">AI Analysis</span>
            </Button>
          </Link>

          <Link href="/visualize">
            <Button variant="outline" className="w-full h-24 flex flex-col items-center justify-center space-y-2">
              <TrendingUp className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Visualize Data</span>
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Recent Datasets */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Datasets</CardTitle>
              <CardDescription>Your latest uploaded datasets</CardDescription>
            </div>
            <Link href="/upload">
              <Button variant="ghost" size="sm">
                View All <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : datasets.length === 0 ? (
            <div className="text-center py-8">
              <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">No datasets yet</p>
              <Link href="/upload">
                <Button>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Your First Dataset
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {datasets.slice(0, 5).map((dataset: any) => (
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
                        {formatNumber(dataset.row_count)} rows × {dataset.column_count} columns
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">
                      {formatDate(dataset.created_at)}
                    </p>
                    <Link href={`/analysis?dataset=${dataset.id}`}>
                      <Button variant="ghost" size="sm" className="mt-1">
                        Analyze <ArrowRight className="ml-1 h-3 w-3" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Getting Started Guide */}
      {datasets.length === 0 && (
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20">
          <CardHeader>
            <CardTitle>Getting Started with VexaAI</CardTitle>
            <CardDescription>Follow these steps to start analyzing your data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <p className="font-medium">Upload Your Data</p>
                <p className="text-sm text-muted-foreground">
                  Upload CSV or Excel files to get started
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <p className="font-medium">Configure AI</p>
                <p className="text-sm text-muted-foreground">
                  Set up your preferred AI model (Grok, Groq, or Gemini)
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <p className="font-medium">Ask Questions</p>
                <p className="text-sm text-muted-foreground">
                  Query your data in plain English and get instant insights
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}