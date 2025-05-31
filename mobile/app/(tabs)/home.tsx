import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Image } from 'expo-image';

export default function HomeScreen() {
    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Image source={require('../../assets/images/brain.png')} style={styles.headerImage} />
                    <Text style={styles.headerText}>PredictMMA</Text>
                </View>
            </View>

            {/* Main Content */}
            <View style={styles.mainContent}>
                <Text style={styles.welcomeTitle}>Welcome Home</Text>
                <Text style={styles.welcomeSubtitle}>
                    This is your home screen
                </Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'light-grey',
    },
    header: {
        backgroundColor: 'white',
        padding: 10,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 50,
    },
    headerImage: {
        width: 36,
        height: 36,
        marginRight: 8,
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    mainContent: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    welcomeTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 8,
    },
    welcomeSubtitle: {
        fontSize: 16,
        color: '#4b5563',
        textAlign: 'center',
    },
});
