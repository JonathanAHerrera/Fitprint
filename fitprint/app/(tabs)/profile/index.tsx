import { useEffect, useState } from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";

export default function ProfileScreen() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = await AsyncStorage.getItem("google_id_token");
        if (!token) return router.replace("/login");

        const response = await fetch("http://YOUR_SERVER_IP:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = await response.json();
        setUser(data);
      } catch (err) {
        Alert.alert("Error", "Could not load profile");
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.removeItem("google_id_token");
    router.replace("/login");
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#FF6FCF" />
      </View>
    );
  }

  if (!user) {
    return (
      <View style={styles.center}>
        <Text style={{ color: "#fff" }}>Not logged in.</Text>
      </View>
    );
  }

  return (
    <LinearGradient colors={["#37306B", "#66347F", "#D27685"]} style={styles.container}>
      {user.picture && <Image source={{ uri: user.picture }} style={styles.avatar} />}

      <Text style={styles.name}>{user.full_name}</Text>
      <Text style={styles.email}>{user.email}</Text>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Change Password</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.button, styles.logoutButton]} onPress={handleLogout}>
        <Text style={[styles.buttonText, { color: "#37306B" }]}>Log Out</Text>
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#37306B" },
  container: { flex: 1, alignItems: "center", paddingTop: 60 },
  avatar: { width: 120, height: 120, borderRadius: 60, borderWidth: 3, borderColor: "#FF6FCF", marginBottom: 20 },
  name: { fontSize: 26, color: "white", fontWeight: "bold", marginBottom: 4, textShadowColor: "rgba(0,0,0,0.3)", textShadowOffset: { width: 2, height: 2 }, textShadowRadius: 4 },
  email: { fontSize: 16, color: "#FFD6E0", marginBottom: 40 },
  button: {
    backgroundColor: "#FF6FCF",
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
    marginTop: 15,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  buttonText: { color: "white", fontSize: 18, fontWeight: "600" },
  logoutButton: { backgroundColor: "#fff" },
});
