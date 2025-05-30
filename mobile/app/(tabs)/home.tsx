import React from 'react';
import { View, Text, SafeAreaView } from 'react-native';

export default function HomeScreen() {
    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header Banner */}
            <View className="bg-blue-500 p-4">
                <Text className="text-white text-center font-bold text-lg">
                    🚀 Welcome to the App!
                </Text>
            </View>

            {/* Main Content */}
            <View className="flex-1 justify-center items-center px-4">
                <Text className="text-2xl font-bold mb-2">Welcome Home</Text>
                <Text className="text-base text-gray-600 text-center">
                    This is your home screen
                </Text>
            </View>
        </SafeAreaView>
    );
}
