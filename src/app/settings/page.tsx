"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"

export default function SettingsPage() {
    const handleClearData = () => {
        if (confirm("Are you sure you want to clear all data? This action cannot be undone.")) {
            // Ideally call API here, but purely frontend for now or minimal implementation
            alert("This feature is placeholder for now.")
        }
    }

    return (
        <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
             <div>
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="text-muted-foreground">Manage your application preferences.</p>
             </div>

             <div className="grid gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>General</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Application Name</label>
                            <div className="p-2 border rounded-md bg-muted text-muted-foreground">
                                Finance Tracker
                            </div>
                        </div>
                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Currency</label>
                            <div className="p-2 border rounded-md bg-muted text-muted-foreground">
                                USD ($)
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Data Management</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="font-medium">Clear Data</h3>
                                <p className="text-sm text-muted-foreground">Remove all expenses and reset local state.</p>
                            </div>
                            <Button 
                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                onClick={handleClearData}
                            >
                                Clear All Data
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Appearance</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="font-medium">Dark Mode</h3>
                                <p className="text-sm text-muted-foreground">Toggle application theme</p>
                            </div>
                            <Button variant="outline" disabled>
                                Enabled (Default)
                            </Button>
                        </div>
                    </CardContent>
                </Card>
             </div>
        </div>
    )
}
