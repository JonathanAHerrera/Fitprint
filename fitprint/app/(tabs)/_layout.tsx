import { Tabs } from "expo-router";
import { Camera, BarChart2, Archive, User } from "lucide-react-native";
import { Platform } from "react-native";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#D27685",
        tabBarInactiveTintColor: "#C9A8D4",
        tabBarStyle: {
          backgroundColor: "#4B3F72",
          borderTopWidth: 0,
          height: Platform.OS === "ios" ? 90 : 70,
          paddingBottom: Platform.OS === "ios" ? 25 : 14,
          paddingTop: 10,
          borderTopLeftRadius: 20,
          borderTopRightRadius: 20,
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          shadowColor: "#000",
          shadowOpacity: 0.15,
          shadowRadius: 8,
          elevation: 5,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "600",
        },
      }}
    >

      <Tabs.Screen
        name="../../capture/index" // <-- path to your page outside tabs
        options={{
          title: "Capture",
          tabBarIcon: ({ color, size }) => <Camera color={color} size={size} />,
        }}
      />

      <Tabs.Screen
        name="../../report/index" // <-- path to report page
        options={{
          title: "Report",
          tabBarIcon: ({ color, size }) => <BarChart2 color={color} size={size} />,
        }}
      />

      <Tabs.Screen
        name="../../wardrobe/index" // <-- path to wardrobe page
        options={{
          title: "Wardrobe",
          tabBarIcon: ({ color, size }) => <Archive color={color} size={size} />,
        }}
      />

      <Tabs.Screen
        name="../../profile/index" // <-- path to profile page
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
        }}
      />

    </Tabs>
  );
}
