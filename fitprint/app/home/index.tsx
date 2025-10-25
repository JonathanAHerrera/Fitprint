import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";

export default function HomeLaunchScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.logo}>FitPrint</Text>
      <Text style={styles.subtitle}>See the impact of your wardrobe.</Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push("/login")}>
        <Text style={styles.buttonText}>Log In</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#37306B",
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  logo: {
    fontSize: 48,
    fontWeight: "700",
    color: "white",
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 18,
    color: "#D27685",
    marginBottom: 40,
    textAlign: "center",
  },
  button: {
    backgroundColor: "#9E4784",
    paddingVertical: 14,
    paddingHorizontal: 40,
    borderRadius: 10,
  },
  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
  },
});
