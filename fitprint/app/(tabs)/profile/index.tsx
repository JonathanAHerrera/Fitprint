import { useEffect, useState } from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";

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
        <ActivityIndicator size="large" color="#9E4784" />
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
    <View style={styles.container}>
      {user.picture && (
        <Image source={{ uri: user.picture }} style={styles.avatar} />
      )}

      <Text style={styles.name}>{user.full_name}</Text>
      <Text style={styles.email}>{user.email}</Text>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Change Password</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.button, styles.logoutButton]} onPress={handleLogout}>
        <Text style={[styles.buttonText, { color: "#37306B" }]}>Log Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#37306B" },
  container: { flex: 1, backgroundColor: "#37306B", alignItems: "center", paddingTop: 60 },
  avatar: { width: 110, height: 110, borderRadius: 55, borderWidth: 3, borderColor: "#9E4784", marginBottom: 20 },
  name: { fontSize: 26, color: "white", fontWeight: "bold", marginBottom: 4 },
  email: { fontSize: 16, color: "#cfcfcf", marginBottom: 40 },
  button: { backgroundColor: "#9E4784", paddingVertical: 14, paddingHorizontal: 32, borderRadius: 10, marginTop: 15 },
  buttonText: { color: "white", fontSize: 18, fontWeight: "600" },
  logoutButton: { backgroundColor: "#fff" },
});
