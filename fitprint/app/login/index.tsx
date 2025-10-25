import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { router } from "expo-router";
import * as Google from "expo-auth-session/providers/google";
import { useEffect } from "react";

export default function LoginScreen() {
  const [request, response, promptAsync] = Google.useAuthRequest({
    clientId: "<YOUR_WEB_CLIENT_ID>", // required for web
    // expoClientId: "<YOUR_EXPO_CLIENT_ID>",
    iosClientId: "<YOUR_IOS_CLIENT_ID>",
    androidClientId: "<YOUR_ANDROID_CLIENT_ID>",
    webClientId: "<YOUR_WEB_CLIENT_ID>",
  });

  useEffect(() => {
    if (response?.type === "success") {
      const { authentication } = response;
      // You can now use authentication.accessToken to fetch user info
      console.log("Google access token:", authentication?.accessToken);
      router.push("/capture"); // Navigate after successful login
    } else if (response?.type === "error") {
      Alert.alert("Login failed", "Could not log in with Google");
    }
  }, [response]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>FitPrint</Text>

      <TextInput placeholder="Email" style={styles.input} />
      <TextInput placeholder="Password" secureTextEntry style={styles.input} />

      <TouchableOpacity style={styles.button} onPress={() => router.push("/capture")}>
        <Text style={styles.buttonText}>Log In</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.button, styles.googleButton]}
        onPress={() => promptAsync()}
      >
        <Text style={[styles.buttonText, { color: "#37306B" }]}>Log in with Google</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#37306B", justifyContent: "center", padding: 30 },
  title: { color: "white", fontSize: 36, textAlign: "center", marginBottom: 40 },
  input: { backgroundColor: "white", borderRadius: 8, padding: 14, marginBottom: 10 },
  button: { backgroundColor: "#9E4784", padding: 14, borderRadius: 8, marginTop: 20, alignItems: "center" },
  buttonText: { color: "white", fontSize: 18, textAlign: "center" },
  googleButton: { backgroundColor: "#fff" },
});
