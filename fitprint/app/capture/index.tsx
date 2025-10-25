import { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert, Platform } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Camera } from "expo-camera";
import { router } from "expo-router";
import { useRef } from "react";

export default function CaptureScreen() {
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const cameraRef = useRef<InstanceType<typeof Camera> | null>(null);

  const requestCameraPermissions = async (): Promise<boolean> => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Permission denied", "Camera permission is required to take photos.");
      return false;
    }
    return true;
  };

  const startCamera = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    if (status === "granted") {
        setHasPermission(true);
        setIsCameraActive(true);
    } else {
        Alert.alert("Permission denied", "Camera access is required to take photos.");
    }
  };

  const snapPhoto = async () => {
    if (cameraRef.current) {
        const photo = await cameraRef.current.takePictureAsync({ quality: 0.8 });
        setPhotoUri(photo.uri);
        setIsCameraActive(false);
    }
  };

  const takePicture = async () => {
    if (Platform.OS !== "web") {
      const hasPermission = await requestCameraPermissions();
      if (!hasPermission) return;
    }

    try {
      const result = await ImagePicker.launchCameraAsync({
        quality: 0.8,
        allowsEditing: false,
        base64: false,
      });

      if (result.assets && result.assets.length > 0) {
        setPhotoUri(result.assets[0].uri);
      } else {
        console.log("User canceled camera.");
      }
    } catch (error) {
      console.error("Error taking photo:", error);
    }
  };

  const pickFromGallery = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        quality: 0.8,
        allowsEditing: false,
        base64: false,
      });

      if (result.assets && result.assets.length > 0) {
        setPhotoUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error("Error picking photo:", error);
    }
  };

  const analyzePhoto = () => {
    if (photoUri) {
      router.push({
        pathname: "/report",
        params: { photo: photoUri },
      });
    }
  };

  return (
    <View style={styles.container}>
        <Text style={styles.header}>Scan Your Clothing</Text>

        {isCameraActive ? (
            <Camera
                style={{ flex: 1, borderRadius: 20 }}
                ref={cameraRef}
            >
                <TouchableOpacity style={styles.snapButton} onPress={snapPhoto}>
                    <Text style={styles.snapText}>📸</Text>
                </TouchableOpacity>
            </Camera>
        ) : photoUri ? (
        <View style={styles.photoContainer}>
            <Image source={{ uri: photoUri }} style={styles.image} />
            <TouchableOpacity style={styles.button} onPress={analyzePhoto}>
            <Text style={styles.buttonText}>Analyze Sustainability</Text>
            </TouchableOpacity>
            <TouchableOpacity
            style={[styles.button, styles.outlineButton]}
            onPress={() => setPhotoUri(null)}
            >
            <Text style={[styles.buttonText, { color: "#9E4784" }]}>Retake Photo</Text>
            </TouchableOpacity>
        </View>
        ) : (
        <View style={styles.captureBoxContainer}>
            <TouchableOpacity style={styles.captureBox} onPress={pickFromGallery}>
            <Text style={styles.captureText}>Tap here to import a photo</Text>
            </TouchableOpacity>

            <View style={styles.verticalButtons}>
            <TouchableOpacity style={styles.button} onPress={startCamera}>
                <Text style={styles.buttonText}>Take Photo</Text>
            </TouchableOpacity>
            <TouchableOpacity
                style={[styles.button, styles.outlineButton]}
                onPress={() => router.push("/wardrobe")}
            >
                <Text style={[styles.buttonText, { color: "#9E4784" }]}>
                Choose from Wardrobe
                </Text>
            </TouchableOpacity>
            </View>
        </View>
        )}
    </View>
    );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#37306B", padding: 20, justifyContent: "center" },
  header: { fontSize: 28, fontWeight: "700", color: "white", textAlign: "center", marginBottom: 20 },
  captureBoxContainer: { alignItems: "center", justifyContent: "center" },
  captureBox: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: "#66347F",
    borderStyle: "dashed",
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  verticalButtons: {
    width: 250,          // match capture box width
    marginTop: 10,
    flexDirection: "column", // stack vertically
    gap: 10,             // spacing between buttons
    alignSelf: "center", // center horizontally
  },
  snapButton: {
  position: "absolute",
  bottom: 20,
  alignSelf: "center",
  backgroundColor: "#9E4784",
  padding: 20,
  borderRadius: 50,
  },
  snapText: { fontSize: 28, color: "#fff" },
  captureText: { color: "#D27685", textAlign: "center" },
  buttonsRow: { flexDirection: "row", justifyContent: "space-between", width: "100%", gap: 10 },
  photoContainer: { alignItems: "center" },
  image: { width: 250, height: 250, borderRadius: 20, marginBottom: 20 },
  button: { flex: 1, backgroundColor: "#9E4784", paddingVertical: 14, borderRadius: 10, marginVertical: 5, alignItems: "center" },
  outlineButton: { backgroundColor: "#fff" },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" },
});
