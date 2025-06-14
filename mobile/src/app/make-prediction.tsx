import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Image } from 'expo-image';
import { useLocalSearchParams, router } from 'expo-router';
import { Fight } from '../types/ufc_types';

export default function MakePredictionScreen() {
    const { fightData } = useLocalSearchParams();
    const fight: Fight = JSON.parse(fightData as string);
    const [selectedFighter, setSelectedFighter] = useState<1 | 2 | null>(null);
    const [selectedMethod, setSelectedMethod] = useState<string | null>(null);

    const formatFighterName = (fullName: string) => {
        const nameParts = fullName.trim().split(' ');
        if (nameParts.length === 1) {
            return { firstName: nameParts[0], lastName: '' };
        }
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(' ');
        return { firstName, lastName };
    };

    const fighter1Name = formatFighterName(fight.fighter_1_name);
    const fighter2Name = formatFighterName(fight.fighter_2_name);

    return (
        <View style={styles.container}>
            {/* Header with back button */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <Text style={styles.backButtonText}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.headerText}>Make Prediction</Text>
                <View style={styles.placeholder} />
            </View>

            {/* Fighters Container */}
            <View style={styles.selectionContainer}>
                <Text style={styles.subtitleText}>{selectedFighter ? 'Fighter' : 'Select Fighter'}</Text>
                <View style={styles.fightersRow}>
                    {/* Fighter 1 */}
                    <TouchableOpacity style={styles.fighterSection} onPress={() => setSelectedFighter(1)} activeOpacity={0.8}>
                        <Image
                            source={{ uri: fight.fighter_1_image }}
                            style={[
                                styles.fighterImage,
                                selectedFighter === 1 && styles.selectedFighterImage
                            ]}
                            contentFit="cover"
                            contentPosition="top"
                        />
                        <View style={styles.fighterNameContainer}>
                            <Text style={styles.fighterName}>
                                {fighter1Name.firstName}
                                {fighter1Name.lastName ? ` ${fighter1Name.lastName}` : ''}
                            </Text>
                        </View>
                    </TouchableOpacity>

                    {/* Fighter 2 */}
                    <TouchableOpacity style={styles.fighterSection} onPress={() => setSelectedFighter(2)} activeOpacity={0.8}>
                        <Image
                            source={{ uri: fight.fighter_2_image }}
                            style={[
                                styles.fighterImage,
                                selectedFighter === 2 && styles.selectedFighterImage
                            ]}
                            contentFit="cover"
                            contentPosition="top"
                        />
                        <View style={styles.fighterNameContainer}>
                            <Text style={styles.fighterName}>
                                {fighter2Name.firstName}
                                {fighter2Name.lastName ? ` ${fighter2Name.lastName}` : ''}
                            </Text>
                        </View>
                    </TouchableOpacity>
                </View>
            </View>
            {selectedFighter && (
                <View style={styles.selectionContainer}>
                    <Text style={styles.subtitleText}>Method of Victory</Text>
                    <View style={styles.methodImagesRow}>
                        {/* Knockout */}
                        <TouchableOpacity style={styles.methodItem} onPress={() => setSelectedMethod('Knockout')} activeOpacity={0.8}>
                            <Image
                                source={require('../../assets/images/punch.png')}
                                style={[
                                    styles.fighterImage,
                                    selectedMethod === 'Knockout' && styles.selectedMethodImage
                                ]}
                                contentFit="cover"
                                contentPosition="center"
                            />
                            <Text style={styles.fighterName}>Knockout</Text>
                        </TouchableOpacity>

                        {/* Submission */}
                        <TouchableOpacity style={styles.methodItem} onPress={() => setSelectedMethod('Submission')} activeOpacity={0.8}>
                            <Image
                                source={require('../../assets/images/choke.png')}
                                style={[
                                    styles.fighterImage,
                                    selectedMethod === 'Submission' && styles.selectedMethodImage
                                ]}
                                contentFit="cover"
                                contentPosition="center"
                            />
                            <Text style={styles.fighterName}>Submission</Text>
                        </TouchableOpacity>

                        {/* Decision */}
                        <TouchableOpacity style={styles.methodItem} onPress={() => setSelectedMethod('Decision')} activeOpacity={0.8}>
                            <Image
                                source={require('../../assets/images/law.png')}
                                style={[
                                    styles.fighterImage,
                                    selectedMethod === 'Decision' && styles.selectedMethodImage
                                ]}
                                contentFit="cover"
                                contentPosition="center"
                            />
                            <Text style={styles.fighterName}>Decision</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            )}
            {(selectedMethod === 'Knockout' || selectedMethod === 'Submission') && (
                <View style={styles.selectionContainer}>
                    <Text style={styles.subtitleText}>Additional Options (Placeholder)</Text>
                    <Text style={styles.fighterName}>
                        This is a placeholder for {selectedMethod} options.
                    </Text>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: 'white',
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
        paddingTop: 60,
    },
    backButton: {
        padding: 8,
    },
    backButtonText: {
        fontSize: 16,
        color: '#007AFF',
        fontWeight: '600',
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    placeholder: {
        width: 50,
    },
    selectionContainer: {
        marginHorizontal: 16,
        marginTop: 16,
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.06,
        shadowRadius: 4,
        elevation: 2,
        alignItems: 'center',
    },
    fightersRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 30,
        marginHorizontal: 16,
    },
    methodImagesRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'flex-start',
        marginTop: 8,
    },
    fighterSection: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: -36,
    },
    fighterImage: {
        width: 70,
        height: 70,
        borderRadius: 35,
        marginBottom: 6,
        backgroundColor: '#fafafa',
        borderWidth: 2,
        borderColor: '#e0e0e0',
        alignSelf: 'center',
    },
    selectedFighterImage: {
        borderColor: '#007AFF',
        borderWidth: 3,
        shadowColor: '#007AFF',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    fighterNameContainer: {
        alignItems: 'center',
        justifyContent: 'center',
        alignSelf: 'center',
    },
    fighterName: {
        fontSize: 13,
        fontWeight: '400',
        textAlign: 'center',
        color: '#222',
    },
    subtitleText: {
        fontSize: 15,
        color: '#666',
        textAlign: 'center',
        marginTop: 8,
        marginBottom: 16,
        fontWeight: '500',
    },
    methodLabel: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#222',
        marginBottom: 8,
    },
    methodItem: {
        alignItems: 'center',
        justifyContent: 'center',
        marginHorizontal: 18,
    },
    selectedMethodImage: {
        borderColor: '#007AFF',
        borderWidth: 3,
        shadowColor: '#007AFF',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
});