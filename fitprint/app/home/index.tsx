import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from "react-native";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Circle, Ellipse } from "react-native-svg";

const { width, height } = Dimensions.get("window");

export default function HomeLaunchScreen() {
  return (
    <View style={styles.container}>
      {/* Background gradient with floating shapes */}
      <LinearGradient
        colors={["#37306B", "#66347F", "#D27685"]}
        style={StyleSheet.absoluteFill}
      />
      <Svg
        height={height}
        width={width}
        style={StyleSheet.absoluteFill}
      >
        <Circle cx={width * 0.2} cy={height * 0.3} r={100} fill="rgba(255,255,255,0.05)" />
        <Ellipse cx={width * 0.8} cy={height * 0.6} rx={120} ry={60} fill="rgba(255,255,255,0.07)" />
        <Circle cx={width * 0.5} cy={height * 0.8} r={80} fill="rgba(255,255,255,0.04)" />
      </Svg>

      <View style={styles.content}>
        <Text style={styles.logo}>FitPrint</Text>
        <Text style={styles.subtitle}>See the impact of your wardrobe.</Text>

        <TouchableOpacity style={styles.button} onPress={() => router.push("/login")}>
          <Text style={styles.buttonText}>Log In</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  logo: {
    fontSize: 48,
    fontWeight: "700",
    color: "white",
    marginBottom: 12,
    textShadowColor: "rgba(0,0,0,0.3)",
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 18,
    color: "#FFD6E0",
    marginBottom: 40,
    textAlign: "center",
  },
  button: {
    backgroundColor: "#FF6FCF",
    paddingVertical: 14,
    paddingHorizontal: 50,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "700",
  },
});
