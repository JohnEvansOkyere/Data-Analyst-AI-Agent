// app/dashboard/admin/page.tsx


"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { useRouter } from "next/navigation";
import { 
  Users, 
  Database, 
  Activity,
  Shield,
  AlertCircle
} from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function AdminPage() {
  const { toast } = useToast();
  const router = useRouter();
  const { user } = useStore();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.is_admin) {
      toast({
        title: "Access Denied",
        description: "You need administrator privileges to access this page",
        variant: "destructive",
      });
      router.push("/dashboard");
      return;
    }

    loadUsers();
  }, [user, router]);

  const loadUsers = async () => {
    try {
      const response = await api.getAllUsers();
      setUsers(response.users || []);
    } catch (error) {
      toast({
        title: "Error loading users",
        description: "Failed to load user list",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_admin) {
    return null;
  }

  const stats = {
    totalUsers: users.length,
    activeUsers: users.filter(u => u.is_active).length,
    adminUsers: users.filter(u => u.role === 'admin').length,
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center">
            <Shield className="h-8 w-8 mr-3 text-red-500" />
            Admin Panel
          </h1>
          <p className="text-muted-foreground text-lg">
            User management and system administration
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeUsers}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Administrators</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.adminUsers}</div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>Manage user accounts and permissions</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : users.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No users found</div>
          ) : (
            <div className="space-y-4">
              {users.map((u) => (
                <div
                  key={u.username}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-primary/10 rounded-full">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <p className="font-medium">{u.full_name || u.username}</p>
                        {u.role === 'admin' && (
                          <Badge variant="destructive">Admin</Badge>
                        )}
                        {!u.is_active && (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {u.email} • @{u.username}
                      </p>
                      {u.created_at && (
                        <p className="text-xs text-muted-foreground">
                          Joined {formatDate(u.created_at)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {u.is_active ? (
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                        Inactive
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
          <CardDescription>VexaAI platform details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <p className="text-sm font-medium">Application</p>
              <p className="text-sm text-muted-foreground">VexaAI Data Analyst Pro v1.0.0</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Database</p>
              <p className="text-sm text-muted-foreground">Supabase (PostgreSQL)</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">AI Providers</p>
              <p className="text-sm text-muted-foreground">xAI Grok, Groq, Google Gemini</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Environment</p>
              <p className="text-sm text-muted-foreground">Production</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}