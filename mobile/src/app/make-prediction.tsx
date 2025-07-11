import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Image } from 'expo-image';
import { useLocalSearchParams, router } from 'expo-router';
import { Fight } from '../types/ufc_types';
import { jwtDecode } from 'jwt-decode';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createPrediction, getPrediction } from '../lib/api/predict_api';

export default function MakePredictionScreen() {
    const { fightData } = useLocalSearchParams();
    const fight: Fight = JSON.parse(fightData as string);
    const fightId = `${fight.fighter_1_name} vs. ${fight.fighter_2_name}`;
    const [selectedFighter, setSelectedFighter] = useState<string | null>(null);
    const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
    const [selectedRound, setSelectedRound] = useState<number | null>(null);

    useEffect(() => {
        const fetchExistingPrediction = async () => {
            try {
                const token = await AsyncStorage.getItem('access_token');
                if (!token) return;

                const decoded: any = jwtDecode(token);
                if (!decoded || !decoded.sub) return;

                const user_id = decoded.sub as number;

                const existingPrediction = await getPrediction(
                    user_id,
                    fight.event_url,
                    fightId,
                    token ?? undefined,
                );

                if (existingPrediction) {
                    setSelectedFighter(existingPrediction.fighter_prediction);
                    setSelectedMethod(existingPrediction.method_prediction);
                    setSelectedRound(existingPrediction.round_prediction);
                }
            } catch (error) {
                console.error('Error fetching existing prediction:', error);
            }
        };

        fetchExistingPrediction();
    }, []);

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

    // Handle submit action (placeholder for now)
    const handleSubmit = async () => {
        try {
            const token = await AsyncStorage.getItem('access_token');

            let user_id: number | null = null;
            if (token) {
                const decoded: any = jwtDecode(token);
                if (decoded && decoded.sub) {
                    user_id = decoded.sub as number;
                }
            }

            if (!user_id || !selectedFighter || !selectedMethod) {
                console.warn('Prediction data is incomplete.');
                return;
            }

            await createPrediction({
                user_id: user_id,
                event_url: fight.event_url,
                fight_id: fightId,
                fight_idx: fight.fight_idx,
                fighter_prediction: selectedFighter,
                method_prediction: selectedMethod,
                round_prediction: selectedRound,
            }, token ?? undefined);

            router.back();
        } catch (error) {
            console.error('Error submitting prediction:', error);
        }
    };

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
                    <TouchableOpacity style={styles.fighterSection} onPress={() => setSelectedFighter(fight.fighter_1_name)} activeOpacity={0.8}>
                        <Image
                            source={{ uri: fight.fighter_1_image }}
                            style={[
                                styles.fighterImage,
                                selectedFighter === fight.fighter_1_name && styles.selectedFighterImage
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
                    <TouchableOpacity style={styles.fighterSection} onPress={() => setSelectedFighter(fight.fighter_2_name)} activeOpacity={0.8}>
                        <Image
                            source={{ uri: fight.fighter_2_image }}
                            style={[
                                styles.fighterImage,
                                selectedFighter === fight.fighter_2_name && styles.selectedFighterImage
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

            { }
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

            {/* Round Selection */}
            {(selectedMethod === 'Knockout' || selectedMethod === 'Submission') && (
                <View style={styles.selectionContainer}>
                    <Text style={styles.subtitleText}>Select Round</Text>
                    <View style={styles.roundImagesRow}>
                        {/* Round 1 */}
                        <TouchableOpacity style={styles.roundItem} onPress={() => setSelectedRound(1)} activeOpacity={0.8}>
                            <View style={[
                                styles.roundImage,
                                selectedRound === 1 && styles.selectedRoundImage
                            ]}>
                                <Image
                                    source={require('../../assets/images/one.png')}
                                    style={styles.roundNumberImage}
                                    contentFit="cover"
                                    contentPosition="center"
                                />
                            </View>
                        </TouchableOpacity>

                        {/* Round 2 */}
                        <TouchableOpacity style={styles.roundItem} onPress={() => setSelectedRound(2)} activeOpacity={0.8}>
                            <View style={[
                                styles.roundImage,
                                selectedRound === 2 && styles.selectedRoundImage
                            ]}>
                                <Image
                                    source={require('../../assets/images/two.png')}
                                    style={styles.roundNumberImage}
                                    contentFit="cover"
                                    contentPosition="center"
                                />
                            </View>
                        </TouchableOpacity>

                        {/* Round 3 */}
                        <TouchableOpacity style={styles.roundItem} onPress={() => setSelectedRound(3)} activeOpacity={0.8}>
                            <View style={[
                                styles.roundImage,
                                selectedRound === 3 && styles.selectedRoundImage
                            ]}>
                                <Image
                                    source={require('../../assets/images/three.png')}
                                    style={styles.roundNumberImage}
                                    contentFit="cover"
                                    contentPosition="center"
                                />
                            </View>
                        </TouchableOpacity>

                        {/* Round 4 */}
                        <TouchableOpacity style={styles.roundItem} onPress={() => setSelectedRound(4)} activeOpacity={0.8}>
                            <View style={[
                                styles.roundImage,
                                selectedRound === 4 && styles.selectedRoundImage
                            ]}>
                                <Image
                                    source={require('../../assets/images/four.png')}
                                    style={styles.roundNumberImage}
                                    contentFit="cover"
                                    contentPosition="center"
                                />
                            </View>
                        </TouchableOpacity>

                        {/* Round 5 */}
                        <TouchableOpacity style={styles.roundItem} onPress={() => setSelectedRound(5)} activeOpacity={0.8}>
                            <View style={[
                                styles.roundImage,
                                selectedRound === 5 && styles.selectedRoundImage
                            ]}>
                                <Image
                                    source={require('../../assets/images/five.png')}
                                    style={styles.roundNumberImage}
                                    contentFit="cover"
                                    contentPosition="center"
                                />
                            </View>
                        </TouchableOpacity>
                    </View>
                </View>
            )}

            {/* Submit Button */}
            {(selectedMethod === 'Decision' || selectedRound) && (
                <TouchableOpacity
                    style={styles.submitButton}
                    onPress={handleSubmit}
                    activeOpacity={0.8}
                >
                    <Text style={styles.submitButtonText}>Submit Prediction</Text>
                </TouchableOpacity>
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
    roundImagesRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'flex-start',
        marginTop: 8,
    },
    roundItem: {
        alignItems: 'center',
        justifyContent: 'center',
        marginHorizontal: 2,
    },
    roundImage: {
        width: 70,
        height: 70,
        borderRadius: 35,
        alignItems: 'center',
        justifyContent: 'center',
    },
    selectedRoundImage: {
        borderColor: '#007AFF',
        borderWidth: 3,
        shadowColor: '#007AFF',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    roundNumberImage: {
        width: 40,
        height: 40,
        borderRadius: 20,
    },
    submitButton: {
        backgroundColor: '#007AFF',
        paddingVertical: 14,
        paddingHorizontal: 32,
        borderRadius: 25,
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 24,
        marginHorizontal: 16,
        alignSelf: 'stretch',
    },
    submitButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
});