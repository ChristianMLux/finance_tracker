"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import AllocationChart from "@/components/dashboard/AllocationChart";
import CashflowChart from "@/components/dashboard/CashflowChart";
import { API_URL } from "@/lib/api";
import { PieChart as PieIcon, Activity } from "lucide-react";
import { Card } from "@/components/ui/Card";

interface DashboardProps {
    refreshTrigger?: number;
}

export function Dashboard({ refreshTrigger = 0 }: DashboardProps) {
    const { token, loading: authLoading, user } = useAuth();
    const [allocationData, setAllocationData] = useState([]);
    const [cashflowData, setCashflowData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        if (!token) return;
        
        try {
            setLoading(true);
            setError(null);
            
            const [allocRes, cashRes] = await Promise.all([
                fetch(`${API_URL}/analytics/allocation`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch(`${API_URL}/analytics/cashflow?days=180`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            if (!allocRes.ok || !cashRes.ok) {
                // Silently handle 401s or other issues if needed, but here we want to know
                console.error("Analytics fetch failed");
                throw new Error("Failed to fetch analytics");
            }

            const allocData = await allocRes.json();
            const cashData = await cashRes.json();

            setAllocationData(allocData);
            setCashflowData(cashData);
        } catch (err) {
            console.error(err);
            setError("Could not load dashboard data.");
        } finally {
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        if (!authLoading && token) {
            fetchData();
        }
    }, [authLoading, token, refreshTrigger, fetchData]);

    // Auth loading state
    if (authLoading) return null;

    // Not logged in state
    if (!user) {
        return (
            <div className="h-48 flex flex-col items-center justify-center gap-2 text-muted-foreground animate-fade-in">
                <span className="text-2xl">🔒</span>
                <span>Log in to see your data...</span>
            </div>
        );
    }

    // Data loading state
    if (loading) return <div className="h-48 flex items-center justify-center text-muted-foreground animate-pulse">Loading stats...</div>;

    if (error) {
        return <div className="text-sm text-destructive">{error}</div>;
    }

    return (
        <div className="grid gap-6 md:grid-cols-2">
            <Card>
                <div className="p-6 flex flex-col gap-1">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <PieIcon className="h-4 w-4" /> Expense Allocation
                    </h3>
                    <p className="text-sm text-muted-foreground">Distribution by category</p>
                </div>
                <div className="p-6 pt-0 pl-0">
                    <AllocationChart data={allocationData} />
                </div>
            </Card>

            <Card>
                <div className="p-6 flex flex-col gap-1">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Activity className="h-4 w-4" /> Monthly Cashflow
                    </h3>
                    <p className="text-sm text-muted-foreground">Trends over last 6 months</p>
                </div>
                <div className="p-6 pt-0 pl-0">
                    <CashflowChart data={cashflowData} />
                </div>
            </Card>
        </div>
    );
}
