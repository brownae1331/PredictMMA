import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, TouchableWithoutFeedback, Keyboard } from 'react-native';
import { loginUser } from '../../lib/api/auth_api';
import { router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const validate = () => {
        if (!username) return 'Username is required.';
        if (!password) return 'Password is required.';
        if (username.length < 3) return 'Username must be at least 3 characters.';
        if (username.length > 30) return 'Username must be at most 30 characters.';
        if (!/^[a-zA-Z0-9_]+$/.test(username)) return 'Username must be alphanumeric (letters, numbers, underscores).';
        if (password.length < 8) return 'Password must be at least 8 characters.';
        return '';
    };

    const handleLogin = async () => {
        setError('');
        const validationError = validate();
        if (validationError) {
            setError(validationError);
            return;
        }
        setLoading(true);
        try {
            const data = await loginUser(username, password);
            await AsyncStorage.setItem('username', username);
            await AsyncStorage.setItem('access_token', data.access_token);
            router.replace('/(tabs)/home');
        } catch (error: any) {
            setError(error.message || 'Login failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f6f8fa' }}>
                <View style={styles.card}>
                    <Text style={styles.title}>Login</Text>
                    {error ? <Text style={styles.errorText}>{error}</Text> : null}
                    <TextInput
                        placeholder="Username"
                        value={username}
                        onChangeText={setUsername}
                        autoCapitalize="none"
                        style={styles.input}
                        placeholderTextColor="#888"
                    />
                    <TextInput
                        placeholder="Password"
                        value={password}
                        onChangeText={setPassword}
                        secureTextEntry
                        style={styles.input}
                        placeholderTextColor="#888"
                    />
                    <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
                        <Text style={styles.buttonText}>{loading ? 'Logging in...' : 'Login'}</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => router.replace('/(auth)/signup')} style={{ marginTop: 16 }}>
                        <Text style={styles.linkText}>Don't have an account? Sign up</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </TouchableWithoutFeedback>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        borderRadius: 16,
        padding: 24,
        width: '100%',
        maxWidth: 400,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
        alignItems: 'center',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        marginBottom: 24,
        color: '#222',
    },
    input: {
        borderWidth: 1,
        borderColor: '#ccc',
        marginBottom: 16,
        padding: 12,
        borderRadius: 8,
        width: '100%',
        fontSize: 16,
        backgroundColor: '#f6f8fa',
    },
    button: {
        backgroundColor: '#007AFF',
        paddingVertical: 14,
        borderRadius: 8,
        width: '100%',
        alignItems: 'center',
        marginTop: 8,
    },
    buttonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
    linkText: {
        color: '#007AFF',
        textAlign: 'center',
        fontSize: 16,
        marginTop: 8,
    },
    errorText: {
        color: 'red',
        marginBottom: 12,
        fontSize: 16,
        textAlign: 'center',
    },
}); 