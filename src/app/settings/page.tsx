"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { useAuth } from "@/context/AuthContext"
import { useState, useEffect } from "react"
import { API_URL } from "@/lib/api"

export default function SettingsPage() {
    const { userData, refreshProfile, user } = useAuth()
    const [fullName, setFullName] = useState("")
    const [isSaving, setIsSaving] = useState(false)

    useEffect(() => {
        if (userData?.full_name) {
            setFullName(userData.full_name)
        }
    }, [userData])

    const handleSaveProfile = async () => {
        alert("DEBUG: Handle Save Called") // Uncomment to verify click
        console.log("Starting profile update...");
        
        if (!user) {
            console.error("No user found in AuthContext");
            alert("Error: You are not logged in (user object is missing). Try refreshing.")
            return
        }
        setIsSaving(true)
        try {
            console.log("Getting token...");
            const token = await user.getIdToken()
            console.log("Token retrieved. API URL:", API_URL);
            
            const url = `${API_URL}/users/me`;
            console.log("Fetching:", url);
            
            const res = await fetch(url, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ full_name: fullName })
            })

            console.log("Response status:", res.status);
            
            if (res.ok) {
                console.log("Update successful");
                await refreshProfile()
                alert("Profile updated!")
            } else {
                const errText = await res.text();
                console.error("Update failed:", res.status, errText);
                alert(`Failed to update profile: ${res.status}`)
            }
        } catch (e) {
            console.error("Error in handleSaveProfile:", e)
            alert("Error updating profile. Check console for details.")
        } finally {
            setIsSaving(false)
        }
    }

    const handleClearData = async () => {
        if (!user) return
        if (confirm("Are you sure you want to clear all data? This action cannot be undone.")) {
             try {
                const token = await user.getIdToken()
                const apiUrl = API_URL
                
                const res = await fetch(`${apiUrl}/users/me/data`, {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                })

                if (res.ok) {
                    alert("All data cleared.")
                    // Optional: refresh data or redirect
                } else {
                    alert("Failed to clear data.")
                }
             } catch (e) {
                 console.error(e)
                 alert("Error clearing data.")
             }
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
                        <CardTitle>Profile</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Full Name (Display Name)</label>
                            <div className="flex gap-2">
                                <input 
                                    type="text" 
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="flex-1 p-2 border rounded-md bg-background"
                                    placeholder="Enter your name"
                                />
                                <Button onClick={handleSaveProfile} disabled={isSaving}>
                                    {isSaving ? "Saving..." : "Save"}
                                </Button>
                            </div>
                        </div>
                        <div className="grid gap-2">
                            <label className="text-sm font-medium">Email</label>
                            <div className="p-2 border rounded-md bg-muted text-muted-foreground">
                                {userData?.email || user?.email || "Loading..."}
                            </div>
                        </div>
                         <div className="grid gap-2">
                            <label className="text-sm font-medium">My Role</label>
                            <div className="p-2 border rounded-md bg-muted text-success-foreground capitalize font-bold">
                                {userData?.role || "Free"} Plan
                            </div>
                        </div>
                    </CardContent>
                </Card>

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
             </div>
        </div>
    )
}
