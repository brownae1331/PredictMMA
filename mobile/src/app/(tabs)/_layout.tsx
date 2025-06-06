import { Tabs } from "expo-router";
import { Ionicons, FontAwesome6, MaterialCommunityIcons } from "@expo/vector-icons";

export default function TabLayout() {
    return (
        <Tabs screenOptions={{
            tabBarActiveTintColor: 'black',
            headerShown: false
        }}>
            <Tabs.Screen
                name="home"
                options={{
                    title: "Home",
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="home" color={color} size={size} />
                    ),
                }}
            />

            <Tabs.Screen
                name="predict"
                options={{
                    title: "Predict",
                    tabBarIcon: ({ color, size }) => (
                        <FontAwesome6 name="brain" color={color} size={size} />
                    ),
                }}
            />

            <Tabs.Screen
                name="fighters"
                options={{
                    title: "Fighters",
                    tabBarIcon: ({ color, size }) => (
                        <MaterialCommunityIcons name="boxing-glove" color={color} size={size} />
                    ),
                }}
            />

            <Tabs.Screen
                name="profile"
                options={{
                    title: "Profile",
                    tabBarIcon: ({ color, size }) => (
                        <Ionicons name="person-sharp" color={color} size={size} />
                    ),
                }}
            />
        </Tabs>
    );
}