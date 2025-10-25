import { useState, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert, Platform } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { router } from "expo-router";

export default function CaptureScreen() {
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [cameraPermission, setCameraPermission] = useState<boolean | null>(null);

  // Check camera permission on mount
  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.getCameraPermissionsAsync();
      setCameraPermission(status === "granted");
    })();
  }, []);

  // Take a new photo using the system camera
  const takePhoto = async () => {
    try {
      // Request permission if not already granted
      if (cameraPermission === null || !cameraPermission) {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        setCameraPermission(status === "granted");
        
        if (status !== "granted") {
          Alert.alert("Permission denied", "Camera access is required to take photos.");
          return;
        }
      }

      // Launch the camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
        allowsEditing: false,
      });

      // Check if user didn't cancel
      if (!result.canceled && result.assets && result.assets.length > 0) {
        setPhotoUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error("Error taking photo:", error);
      Alert.alert("Error", "Failed to take photo. Please try again.");
    }
  };

  // Pick an image from gallery
  const pickFromGallery = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
        allowsEditing: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setPhotoUri(result.assets[0].uri);
      }
    } catch (error) {
      console.error("Error picking photo:", error);
      Alert.alert("Error", "Failed to pick photo. Please try again.");
    }
  };

  // Analyze selected photo
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

      {photoUri ? (
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
            <TouchableOpacity style={styles.button} onPress={takePhoto}>
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
  container: {
    flex: 1,
    backgroundColor: "#37306B",
    padding: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    fontSize: 28,
    fontWeight: "700",
    color: "white",
    textAlign: "center",
    marginBottom: 20,
  },
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
  captureText: { color: "#D27685", textAlign: "center" },
  verticalButtons: {
    width: 250,
    marginTop: 10,
    flexDirection: "column",
    gap: 10,
  },
  photoContainer: { alignItems: "center" },
  image: { width: 250, height: 250, borderRadius: 20, marginBottom: 20 },
  button: {
    backgroundColor: "#9E4784",
    paddingVertical: 14,
    borderRadius: 10,
    marginVertical: 5,
    alignItems: "center",
    width: 250,
  },
  outlineButton: { backgroundColor: "#fff" },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" },
});
