"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { 
  User, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signOut as firebaseSignOut,
  onIdTokenChanged 
} from "firebase/auth";
import { auth } from "@/lib/firebase/firebase";
import { useRouter } from "next/navigation";
import { API_URL } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  userData: any | null;
  token: string | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  userData: null,
  token: null,
  loading: true,
  signInWithGoogle: async () => {},
  signOut: async () => {},
  refreshProfile: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [userData, setUserData] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchUserProfile = async (currentUser: User) => {
      try {
          const token = await currentUser.getIdToken();
          const apiUrl = API_URL;
          
          const res = await fetch(`${apiUrl}/users/me`, {
              headers: {
                  Authorization: `Bearer ${token}`
              }
          });
          
          if (res.ok) {
              const data = await res.json();
              setUserData(data);
          }
      } catch (e) {
          console.error("Failed to fetch user profile", e);
          // Don't get stuck loading
      }
  };

  useEffect(() => {
    const unsubscribe = onIdTokenChanged(auth, async (user) => {
      console.log("Auth: State changed", user ? user.uid : "No user");
      setUser(user);
      if (user) {
        try {
            console.log("Auth: Getting token...");
            const t = await user.getIdToken();
            console.log("Auth: Token acquired");
            setToken(t);
            console.log("Auth: Fetching profile...");
            await fetchUserProfile(user);
            console.log("Auth: Profile fetched");
        } catch (err) {
            console.error("Auth: Error validation flow", err);
        }
      } else {
        setToken(null);
        setUserData(null);
      }
      setLoading(false);
      console.log("Auth: Loading set to false");
    });

    return () => unsubscribe();
  }, []);

  const refreshProfile = async () => {
      if (user) {
          await fetchUserProfile(user);
      }
  }

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      router.push("/"); 
    } catch (error) {
      console.error("Error signing in with Google", error);
    }
  };

  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
      setToken(null);
      setUserData(null);
      router.push("/login"); 
    } catch (error) {
      console.error("Error signing out", error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, userData, token, loading, signInWithGoogle, signOut, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
